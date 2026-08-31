import logging
from typing import cast
from urllib.parse import urlencode

from authlib.integrations.base_client.errors import OAuthError  # type: ignore[import-untyped]
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.config import get_settings
from app.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUserRead
from app.services.auth import auth_service
from app.services.errors import (
    MatrixIdentityConflictError,
    MatrixIdentityError,
    MatrixProfileError,
    TokenEncryptionError,
)
from app.services.auth.matrix_identity import get_matrix_identity
from app.services.auth.matrix_profile import (
    MatrixProfile,
    get_matrix_profile,
)

from app.services.matrix_oauth import get_matrix_oauth_client
from app.services.token_encryption import get_token_cipher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _encrypt_refresh_token(refresh_token: str | None) -> str | None:
    """Encrypt the refresh token, treating avatar support as optional.

    The avatar proxy is enrichment. A deployment whose OAuth client lacks the
    refresh_token grant must still be able to sign in, exactly as it does when
    a homeserver disables profile lookup.
    """
    if refresh_token is None:
        logger.warning(
            "Matrix login returned no refresh token; avatars will be unavailable. "
            "Register the OAuth client for the refresh_token grant to enable them."
        )
        return None

    try:
        return get_token_cipher().encrypt(refresh_token)
    except TokenEncryptionError:
        logger.exception("Could not encrypt the Matrix refresh token")
        return None


@router.get("/matrix/login")
async def start_matrix_login(request: Request) -> Response:
    if not settings.matrix_login_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Matrix login is not configured",
        )

    client = get_matrix_oauth_client()
    callback = settings.matrix_oidc_redirect_uri or request.url_for(
        "complete_matrix_login"
    )
    return cast(Response, await client.authorize_redirect(request, callback))


@router.get("/matrix/callback")
async def complete_matrix_login(
    request: Request,
    session: Session = Depends(get_session),
) -> Response:
    homeserver_url = settings.matrix_homeserver_url
    if not settings.matrix_login_configured or homeserver_url is None:
        query = urlencode({"error": "Matrix login is not configured."})
        return RedirectResponse(
            f"{settings.frontend_origin}/login?{query}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    client = get_matrix_oauth_client()
    try:
        token = await client.authorize_access_token(request)
        subject = token["userinfo"]["sub"]
        access_token = token["access_token"]
        matrix_identity = await get_matrix_identity(
            homeserver_url,
            access_token,
        )
    except (KeyError, MatrixIdentityError, OAuthError):
        query = urlencode({"error": "Matrix login failed. Please try again."})
        return RedirectResponse(
            f"{settings.frontend_origin}/login?{query}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    try:
        matrix_profile = await get_matrix_profile(
            homeserver_url,
            matrix_identity.user_id,
        )
    except MatrixProfileError:
        # Profile lookup can be disabled by a homeserver. It is enrichment,
        # not part of proving which Matrix account owns the access token.
        matrix_profile = MatrixProfile()

    avatar_mxc = (
        matrix_profile.avatar_url
        if matrix_profile.avatar_url and matrix_profile.avatar_url.startswith("mxc://")
        else None
    )
    refresh_token_encrypted = _encrypt_refresh_token(token.get("refresh_token"))

    try:
        session_token = auth_service.create_session(
            session,
            issuer=settings.matrix_oidc_issuer,
            subject=subject,
            matrix_id=matrix_identity.user_id,
            matrix_display_name=matrix_profile.displayname,
            matrix_avatar_mxc=avatar_mxc,
            matrix_refresh_token_encrypted=refresh_token_encrypted,
        )
    except MatrixIdentityConflictError:
        query = urlencode({"error": "Matrix login failed. Please try again."})
        return RedirectResponse(
            f"{settings.frontend_origin}/login?{query}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    response = RedirectResponse(
        f"{settings.frontend_origin}/dashboard",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        auth_service.SESSION_COOKIE,
        session_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=auth_service.SESSION_MAX_AGE,
        path="/",
    )
    return response


@router.get("/me", response_model=CurrentUserRead)
def current_user(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session: Session = Depends(get_session),
    session_token: str | None = Cookie(
        default=None,
        alias=auth_service.SESSION_COOKIE,
    ),
) -> None:
    if session_token is not None:
        auth_service.revoke_session(session, token=session_token)
    response.delete_cookie(auth_service.SESSION_COOKIE, path="/")
