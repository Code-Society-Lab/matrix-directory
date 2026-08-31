import pytest
from sqlmodel import Session, select

from app.models.profile import Profile
from app.services.avatar import resolve_avatar_url
from app.services.auth.auth_service import (
    create_session,
    get_matrix_refresh_token_encrypted,
    get_user_for_token,
)
from app.services.errors import (
    MatrixIdentityConflictError,
)


def test_oidc_identity__expect_local_session_created(session: Session) -> None:
    token = create_session(
        session,
        issuer="https://account.matrix.org/",
        subject="opaque-subject",
        matrix_id="@owner:example.org",
    )

    user = get_user_for_token(session, token=token)
    assert user is not None
    assert user.oidc_subject == "opaque-subject"
    assert user.profile is not None
    assert user.profile.matrix_id == "@owner:example.org"


def test_repeated_oidc_identity__expect_local_user_reused(session: Session) -> None:
    first = get_user_for_token(
        session,
        token=create_session(
            session,
            issuer="issuer",
            subject="subject",
            matrix_id="@owner:example.org",
        ),
    )
    second = get_user_for_token(
        session,
        token=create_session(
            session,
            issuer="issuer",
            subject="subject",
            matrix_id="@owner:example.org",
        ),
    )

    assert first is not None
    assert second is not None
    assert first.id == second.id


def test_matrix_identity__expect_profile_verified_from_whoami_result(
    session: Session,
) -> None:
    token = create_session(
        session,
        issuer="issuer",
        subject="subject",
        matrix_id="@owner:example.org",
        matrix_display_name="Matrix Owner",
        matrix_avatar_mxc="mxc://example.org/avatar",
        matrix_refresh_token_encrypted="encrypted-refresh-token",
    )

    user = get_user_for_token(session, token=token)

    assert user is not None
    assert user.profile is not None
    assert user.profile.matrix_id == "@owner:example.org"
    assert user.profile.matrix_id_verified is True
    assert user.profile.display_name == "Matrix Owner"
    # The proxy URL is derived on read, never persisted onto the profile.
    assert user.profile.avatar_url is None
    assert user.profile.matrix_avatar_mxc == "mxc://example.org/avatar"
    assert resolve_avatar_url(user.profile) == f"/api/profiles/{user.id}/avatar"
    assert (
        get_matrix_refresh_token_encrypted(
            session,
            user_id=user.id,
        )
        == "encrypted-refresh-token"
    )


def test_matrix_profile__expect_existing_local_customizations_preserved(
    session: Session,
) -> None:
    token = create_session(
        session,
        issuer="issuer",
        subject="subject",
        matrix_id="@owner:example.org",
        matrix_display_name="Original Matrix Name",
    )
    user = get_user_for_token(session, token=token)
    assert user is not None
    assert user.profile is not None
    user.profile.display_name = "Directory Name"
    session.add(user.profile)
    session.commit()

    create_session(
        session,
        issuer="issuer",
        subject="subject",
        matrix_id="@owner:example.org",
        matrix_display_name="Updated Matrix Name",
    )

    session.refresh(user.profile)
    assert user.profile.display_name == "Directory Name"


def test_matrix_identity__expect_one_verified_owner_per_matrix_id(
    session: Session,
) -> None:
    create_session(
        session,
        issuer="issuer",
        subject="first-subject",
        matrix_id="@owner:example.org",
    )

    with pytest.raises(MatrixIdentityConflictError):
        create_session(
            session,
            issuer="issuer",
            subject="second-subject",
            matrix_id="@owner:example.org",
        )

    session.rollback()
    assert (
        session.exec(select(Profile).where(Profile.matrix_id == "@owner:example.org"))
        .one()
        .user_id
    )
