import asyncio
from uuid import UUID, uuid4

import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.auth import MatrixOAuthCredential
from app.models.profile import Profile
from app.models.user import User
from app.routers.profile_router import get_public_avatar
from app.services import matrix_avatar
from app.services.errors import (
    MatrixAvatarConfigurationError,
    MatrixAvatarUnavailableError,
    MatrixOAuthTokenError,
)
from app.services.matrix_media import MatrixMediaStream
from app.services.matrix_oauth import MatrixOAuthToken
from app.services.token_encryption import TokenCipher

ENCRYPTION_KEY = Fernet.generate_key().decode("utf-8")
CIPHER = TokenCipher(ENCRYPTION_KEY)


class FakeSettings:
    matrix_homeserver_url = "https://matrix.example.com"
    matrix_token_encryption_key = ENCRYPTION_KEY
    matrix_media_configured = True


@pytest.fixture(autouse=True)
def configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(matrix_avatar, "get_settings", lambda: FakeSettings())
    monkeypatch.setattr(matrix_avatar, "get_token_cipher", lambda: CIPHER)
    matrix_avatar._access_token_cache.clear()


def make_user(
    session: Session,
    *,
    avatar_mxc: str | None = "mxc://matrix.org/avatar",
    refresh_token: str | None = "refresh-token",
) -> UUID:
    user = User(oidc_issuer="issuer", oidc_subject=str(uuid4()))
    session.add(user)
    session.flush()
    session.add(
        Profile(
            user_id=user.id,
            matrix_id=f"@{user.id}:example.org",
            matrix_avatar_mxc=avatar_mxc,
        )
    )
    if refresh_token is not None:
        session.add(
            MatrixOAuthCredential(
                user_id=user.id,
                refresh_token_encrypted=CIPHER.encrypt(refresh_token),
            )
        )
    session.commit()
    return user.id


def stub_stream(monkeypatch: pytest.MonkeyPatch, calls: list[str]) -> None:
    async def open_stream(
        *,
        homeserver_url: str,
        access_token: str,
        mxc_uri: str,
    ) -> MatrixMediaStream:
        calls.append(access_token)
        request = httpx.Request("GET", homeserver_url)
        return MatrixMediaStream(
            client=httpx.AsyncClient(),
            response=httpx.Response(200, content=b"png", request=request),
            media_type="image/png",
        )

    monkeypatch.setattr(matrix_avatar, "open_matrix_thumbnail_stream", open_stream)


def stub_refresh(
    monkeypatch: pytest.MonkeyPatch,
    tokens: list[MatrixOAuthToken],
) -> list[str]:
    redeemed: list[str] = []

    async def refresh(refresh_token: str) -> MatrixOAuthToken:
        redeemed.append(refresh_token)
        if not tokens:
            raise MatrixOAuthTokenError("no more tokens")
        return tokens.pop(0)

    monkeypatch.setattr(matrix_avatar, "refresh_matrix_access_token", refresh)
    return redeemed


def test_open_avatar_stream__rotates_and_persists_the_refresh_token(
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = make_user(session)
    redeemed = stub_refresh(
        monkeypatch,
        [
            MatrixOAuthToken(
                access_token="access-1",
                refresh_token="rotated",
                expires_in=300,
            )
        ],
    )
    calls: list[str] = []
    stub_stream(monkeypatch, calls)

    media = asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=user_id))
    asyncio.run(media.close())

    assert redeemed == ["refresh-token"]
    assert calls == ["access-1"]

    credential = session.exec(
        select(MatrixOAuthCredential).where(MatrixOAuthCredential.user_id == user_id)
    ).one()
    assert CIPHER.decrypt(credential.refresh_token_encrypted) == "rotated"


def test_open_avatar_stream__reuses_the_cached_access_token(
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = make_user(session)
    redeemed = stub_refresh(
        monkeypatch,
        [
            MatrixOAuthToken(
                access_token="access-1",
                refresh_token="rotated",
                expires_in=300,
            )
        ],
    )
    calls: list[str] = []
    stub_stream(monkeypatch, calls)

    for _ in range(3):
        media = asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=user_id))
        asyncio.run(media.close())

    # A single-use refresh token must be redeemed once, not once per request.
    assert redeemed == ["refresh-token"]
    assert calls == ["access-1", "access-1", "access-1"]


def test_open_avatar_stream__without_a_matrix_avatar_is_unavailable(
    session: Session,
) -> None:
    user_id = make_user(session, avatar_mxc=None)

    with pytest.raises(MatrixAvatarUnavailableError):
        asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=user_id))


def test_open_avatar_stream__without_a_credential_is_unavailable(
    session: Session,
) -> None:
    user_id = make_user(session, refresh_token=None)

    with pytest.raises(MatrixAvatarUnavailableError):
        asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=user_id))


def test_open_avatar_stream__for_an_unknown_user_is_unavailable(
    session: Session,
) -> None:
    with pytest.raises(MatrixAvatarUnavailableError):
        asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=uuid4()))


def test_open_avatar_stream__when_unconfigured_is_a_configuration_error(
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Unconfigured:
        matrix_homeserver_url = None
        matrix_token_encryption_key = None
        matrix_media_configured = False

    monkeypatch.setattr(matrix_avatar, "get_settings", lambda: Unconfigured())

    with pytest.raises(MatrixAvatarConfigurationError):
        asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=uuid4()))


def test_open_avatar_stream__failed_refresh_clears_the_cached_token(
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = make_user(session)
    stub_refresh(monkeypatch, [])
    stub_stream(monkeypatch, [])

    with pytest.raises(MatrixAvatarUnavailableError):
        asyncio.run(matrix_avatar.open_avatar_stream(session, user_id=user_id))

    assert matrix_avatar._cached_access_token(user_id) is None


def test_disconnect_matrix_avatar__deletes_the_stored_credential(
    session: Session,
) -> None:
    user_id = make_user(session)

    matrix_avatar.disconnect_matrix_avatar(session, user_id=user_id)

    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).one()
    assert profile.matrix_avatar_mxc is None
    assert (
        session.exec(
            select(MatrixOAuthCredential).where(
                MatrixOAuthCredential.user_id == user_id
            )
        ).first()
        is None
    )


def test_get_public_avatar__maps_unavailable_to_404(
    session: Session,
) -> None:
    user_id = make_user(session, avatar_mxc=None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_public_avatar(user_id, session))

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_public_avatar__maps_misconfiguration_to_503(
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Unconfigured:
        matrix_homeserver_url = None
        matrix_token_encryption_key = None
        matrix_media_configured = False

    monkeypatch.setattr(matrix_avatar, "get_settings", lambda: Unconfigured())

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_public_avatar(uuid4(), session))

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_get_public_avatar__sets_hardening_headers(
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = make_user(session)
    stub_refresh(
        monkeypatch,
        [MatrixOAuthToken(access_token="access-1", refresh_token="rotated")],
    )
    stub_stream(monkeypatch, [])

    response = asyncio.run(get_public_avatar(user_id, session))

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.media_type == "image/png"
