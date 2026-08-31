"""Serve Matrix avatars without exposing a Matrix credential to the browser."""

import logging
import time
from dataclasses import dataclass
from uuid import UUID

import httpx
from sqlmodel import Session, select
from starlette.concurrency import run_in_threadpool

from app.config import get_settings
from app.models.auth import MatrixOAuthCredential, utc_now
from app.models.profile import Profile

from .errors import (
    MatrixAvatarConfigurationError,
    MatrixAvatarUnavailableError,
    MatrixMediaError,
    MatrixOAuthTokenError,
    TokenEncryptionError,
)
from .matrix_media import MatrixMediaStream, open_matrix_thumbnail_stream
from .matrix_oauth import MatrixOAuthToken, refresh_matrix_access_token
from .token_encryption import TokenCipher, get_token_cipher

logger = logging.getLogger(__name__)

# Refresh tokens are single use. Caching the short-lived access token stops a
# burst of avatar requests from redeeming the same refresh token repeatedly,
# which an authorization server is entitled to treat as replay.
_DEFAULT_ACCESS_TOKEN_TTL = 300.0
_EXPIRY_SAFETY_MARGIN = 30.0

_access_token_cache: dict[UUID, "_CachedAccessToken"] = {}


@dataclass(frozen=True)
class _CachedAccessToken:
    access_token: str
    expires_at: float


def forget_access_token(user_id: UUID) -> None:
    """Drop a cached access token so the next request obtains a fresh one."""
    _access_token_cache.pop(user_id, None)


def _cached_access_token(user_id: UUID) -> str | None:
    cached = _access_token_cache.get(user_id)
    if cached is None:
        return None

    if cached.expires_at <= time.monotonic():
        forget_access_token(user_id)
        return None

    return cached.access_token


def _remember_access_token(user_id: UUID, token: MatrixOAuthToken) -> None:
    ttl = float(token.expires_in or _DEFAULT_ACCESS_TOKEN_TTL)
    _access_token_cache[user_id] = _CachedAccessToken(
        access_token=token.access_token,
        expires_at=time.monotonic() + max(ttl - _EXPIRY_SAFETY_MARGIN, 0.0),
    )


def _load_avatar_mxc(session: Session, user_id: UUID) -> str | None:
    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    return profile.matrix_avatar_mxc if profile is not None else None


def _lock_credential(session: Session, user_id: UUID) -> MatrixOAuthCredential:
    """Read the credential row and hold it until the transaction completes."""
    credential = session.exec(
        select(MatrixOAuthCredential)
        .where(MatrixOAuthCredential.user_id == user_id)
        .with_for_update()
    ).first()
    if credential is None:
        raise MatrixAvatarUnavailableError("No Matrix credential for this user")

    return credential


def _store_rotated_refresh_token(
    session: Session,
    *,
    credential: MatrixOAuthCredential,
    cipher: TokenCipher,
    token: MatrixOAuthToken,
) -> None:
    if token.refresh_token is not None:
        credential.refresh_token_encrypted = cipher.encrypt(token.refresh_token)
        credential.updated_at = utc_now()
        session.add(credential)

    session.commit()


async def _obtain_access_token(session: Session, user_id: UUID) -> str:
    """Redeem the stored refresh token and persist the rotated replacement.

    The credential row stays locked across the token exchange so that two
    concurrent avatar requests cannot redeem the same single-use refresh token.
    """
    cipher = get_token_cipher()
    credential = await run_in_threadpool(_lock_credential, session, user_id)
    refresh_token = cipher.decrypt(credential.refresh_token_encrypted)

    try:
        token = await refresh_matrix_access_token(refresh_token)
    except MatrixOAuthTokenError:
        await run_in_threadpool(session.rollback)
        raise

    await run_in_threadpool(
        _store_rotated_refresh_token,
        session,
        credential=credential,
        cipher=cipher,
        token=token,
    )
    _remember_access_token(user_id, token)

    return token.access_token


async def open_avatar_stream(
    session: Session,
    *,
    user_id: UUID,
) -> MatrixMediaStream:
    """Open an authenticated thumbnail stream for a user's Matrix avatar."""
    settings = get_settings()
    homeserver_url = settings.matrix_homeserver_url
    if not settings.matrix_media_configured or homeserver_url is None:
        raise MatrixAvatarConfigurationError("Matrix media proxying is not configured")

    mxc_uri = await run_in_threadpool(_load_avatar_mxc, session, user_id)
    if mxc_uri is None:
        raise MatrixAvatarUnavailableError("No Matrix avatar for this user")

    access_token = _cached_access_token(user_id)
    was_cached = access_token is not None

    try:
        if access_token is None:
            access_token = await _obtain_access_token(session, user_id)

        try:
            return await open_matrix_thumbnail_stream(
                homeserver_url=homeserver_url,
                access_token=access_token,
                mxc_uri=mxc_uri,
            )
        except httpx.HTTPStatusError:
            if not was_cached:
                raise

            # The cached token was rejected before its advertised expiry.
            forget_access_token(user_id)
            return await open_matrix_thumbnail_stream(
                homeserver_url=homeserver_url,
                access_token=await _obtain_access_token(session, user_id),
                mxc_uri=mxc_uri,
            )
    except (
        MatrixMediaError,
        MatrixOAuthTokenError,
        TokenEncryptionError,
        httpx.HTTPError,
    ) as exc:
        forget_access_token(user_id)
        logger.warning(
            "Matrix avatar unavailable for user %s: %s",
            user_id,
            exc,
            exc_info=True,
        )
        raise MatrixAvatarUnavailableError("Could not load the Matrix avatar") from exc


def disconnect_matrix_avatar(session: Session, *, user_id: UUID) -> None:
    """Forget the Matrix avatar and delete the stored credential for a user.

    The credential exists only to serve that avatar, so this is the user-facing
    revocation path: nothing keeps a refreshable Matrix token afterwards.
    """
    profile = session.exec(select(Profile).where(Profile.user_id == user_id)).first()
    if profile is not None:
        profile.matrix_avatar_mxc = None
        profile.updated_at = utc_now()
        session.add(profile)

    credential = session.exec(
        select(MatrixOAuthCredential).where(MatrixOAuthCredential.user_id == user_id)
    ).first()
    if credential is not None:
        session.delete(credential)

    forget_access_token(user_id)
    session.commit()
