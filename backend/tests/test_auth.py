from sqlmodel import Session

from app.services.auth_service import create_session, get_user_for_token


def test_oidc_identity__expect_local_session_created(session: Session) -> None:
    token = create_session(
        session,
        issuer="https://account.matrix.org/",
        subject="opaque-subject",
    )

    user = get_user_for_token(session, token=token)
    assert user is not None
    assert user.oidc_subject == "opaque-subject"
    assert user.profile is None


def test_repeated_oidc_identity__expect_local_user_reused(session: Session) -> None:
    first = get_user_for_token(
        session,
        token=create_session(session, issuer="issuer", subject="subject"),
    )
    second = get_user_for_token(
        session,
        token=create_session(session, issuer="issuer", subject="subject"),
    )

    assert first is not None
    assert second is not None
    assert first.id == second.id
