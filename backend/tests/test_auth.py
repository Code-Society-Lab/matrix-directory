from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.services.auth_service import create_session, get_user_for_token


def make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_oidc_identity_creates_local_session() -> None:
    with make_session() as session:
        token = create_session(
            session,
            issuer="https://account.matrix.org/",
            subject="opaque-subject",
        )

        user = get_user_for_token(session, token=token)
        assert user is not None
        assert user.oidc_subject == "opaque-subject"
        assert user.matrix_id is None


def test_same_oidc_identity_reuses_local_user() -> None:
    with make_session() as session:
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
