import hashlib
import secrets
from datetime import timedelta

from sqlmodel import Session, select

from app.models.auth import AuthSession, utc_now
from app.models.user import User

SESSION_COOKIE = "matrix_directory_session"
SESSION_MAX_AGE = 7 * 24 * 60 * 60


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _get_auth_session(session: Session, token: str) -> AuthSession | None:
    return session.exec(
        select(AuthSession).where(AuthSession.token_hash == hash_secret(token))
    ).first()


def create_session(session: Session, *, issuer: str, subject: str) -> str:
    user = session.exec(
        select(User).where(
            User.oidc_issuer == issuer,
            User.oidc_subject == subject,
        )
    ).first()
    if user is None:
        user = User(oidc_issuer=issuer, oidc_subject=subject)
        session.add(user)
        session.flush()

    raw_session_token = secrets.token_urlsafe(48)
    auth_session = AuthSession(
        token_hash=hash_secret(raw_session_token),
        user_id=user.id,
        expires_at=utc_now() + timedelta(seconds=SESSION_MAX_AGE),
    )
    session.add(auth_session)
    session.commit()
    return raw_session_token


def get_user_for_token(session: Session, *, token: str) -> User | None:
    auth_session = _get_auth_session(session, token)
    if auth_session is None or auth_session.expires_at <= utc_now():
        return None
    return session.get(User, auth_session.user_id)


def revoke_session(session: Session, *, token: str) -> None:
    auth_session = _get_auth_session(session, token)
    if auth_session is not None:
        session.delete(auth_session)
        session.commit()
