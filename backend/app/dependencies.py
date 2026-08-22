from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.services.auth.auth_service import SESSION_COOKIE, get_user_for_token


def get_current_user(
    session: Session = Depends(get_session),
    session_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE,
    ),
) -> User:
    """Get the currently authenticated user based on the session token cookie."""

    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user = get_user_for_token(session, token=session_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return user
