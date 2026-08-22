import hashlib
import secrets
from datetime import timedelta

from sqlmodel import Session, select

from app.models.auth import AuthSession, utc_now
from app.models.profile import Profile
from app.models.user import User
from ..errors import MatrixIdentityConflictError

SESSION_COOKIE = "matrix_directory_session"
SESSION_MAX_AGE = 7 * 24 * 60 * 60  # 7 days validity


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _get_auth_session(session: Session, token: str) -> AuthSession | None:
    return session.exec(
        select(AuthSession).where(AuthSession.token_hash == hash_secret(token))
    ).first()


def create_session(
    session: Session,
    *,
    issuer: str,
    subject: str,
    matrix_id: str,
    matrix_display_name: str | None = None,
) -> str:
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

    conflicting_profile = session.exec(
        select(Profile).where(
            Profile.matrix_id == matrix_id,
            Profile.user_id != user.id,
        )
    ).first()
    if conflicting_profile is not None:
        raise MatrixIdentityConflictError(
            "Matrix identity is already associated with another account"
        )

    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
    if profile is None:
        profile = Profile(
            user_id=user.id,
            matrix_id=matrix_id,
            display_name=matrix_display_name,
        )
    elif profile.display_name is None:
        profile.display_name = matrix_display_name

    profile.matrix_id = matrix_id
    profile.matrix_id_verified = True
    profile.updated_at = utc_now()
    session.add(profile)

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
