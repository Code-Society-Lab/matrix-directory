import hashlib
import secrets
from datetime import timedelta
from uuid import UUID

from sqlmodel import Session, select

from app.models.auth import AuthSession, MatrixOAuthCredential, utc_now
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


def get_matrix_refresh_token_encrypted(
    session: Session,
    *,
    user_id: UUID,
) -> str | None:
    """Return the encrypted Matrix refresh token for a local user."""
    credential = session.exec(
        select(MatrixOAuthCredential).where(MatrixOAuthCredential.user_id == user_id)
    ).first()
    return credential.refresh_token_encrypted if credential is not None else None


def store_matrix_refresh_token_encrypted(
    session: Session,
    *,
    user_id: UUID,
    encrypted_token: str,
) -> None:
    """Create or rotate a user's encrypted Matrix refresh token."""
    credential = session.exec(
        select(MatrixOAuthCredential).where(MatrixOAuthCredential.user_id == user_id)
    ).first()
    if credential is None:
        credential = MatrixOAuthCredential(
            user_id=user_id,
            refresh_token_encrypted=encrypted_token,
        )
    else:
        credential.refresh_token_encrypted = encrypted_token
        credential.updated_at = utc_now()
    session.add(credential)


def _get_or_create_user(session: Session, *, issuer: str, subject: str) -> User:
    user = session.exec(
        select(User).where(
            User.oidc_issuer == issuer,
            User.oidc_subject == subject,
        )
    ).first()
    if user is not None:
        return user

    user = User(oidc_issuer=issuer, oidc_subject=subject)
    session.add(user)
    session.flush()
    return user


def _require_unclaimed_matrix_id(
    session: Session,
    *,
    user: User,
    matrix_id: str,
) -> None:
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


def _upsert_verified_profile(
    session: Session,
    *,
    user: User,
    matrix_id: str,
    matrix_display_name: str | None,
    matrix_avatar_mxc: str | None,
) -> Profile:
    """Record the homeserver-verified identity without overwriting local edits."""
    profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
    if profile is None:
        profile = Profile(
            user_id=user.id,
            matrix_id=matrix_id,
            display_name=matrix_display_name,
        )
    elif profile.display_name is None:
        profile.display_name = matrix_display_name

    if matrix_avatar_mxc is not None:
        profile.matrix_avatar_mxc = matrix_avatar_mxc

    profile.matrix_id = matrix_id
    profile.matrix_id_verified = True
    profile.updated_at = utc_now()
    session.add(profile)
    return profile


def _issue_session_token(session: Session, *, user: User) -> str:
    raw_session_token = secrets.token_urlsafe(48)
    session.add(
        AuthSession(
            token_hash=hash_secret(raw_session_token),
            user_id=user.id,
            expires_at=utc_now() + timedelta(seconds=SESSION_MAX_AGE),
        )
    )
    return raw_session_token


def create_session(
    session: Session,
    *,
    issuer: str,
    subject: str,
    matrix_id: str,
    matrix_display_name: str | None = None,
    matrix_avatar_mxc: str | None = None,
    matrix_refresh_token_encrypted: str | None = None,
) -> str:
    """Resolve the local account for a verified Matrix identity and sign it in."""
    user = _get_or_create_user(session, issuer=issuer, subject=subject)

    _require_unclaimed_matrix_id(session, user=user, matrix_id=matrix_id)
    _upsert_verified_profile(
        session,
        user=user,
        matrix_id=matrix_id,
        matrix_display_name=matrix_display_name,
        matrix_avatar_mxc=matrix_avatar_mxc,
    )

    if matrix_refresh_token_encrypted is not None:
        store_matrix_refresh_token_encrypted(
            session,
            user_id=user.id,
            encrypted_token=matrix_refresh_token_encrypted,
        )

    raw_session_token = _issue_session_token(session, user=user)
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
