from typing import cast
from urllib.parse import urlencode

from authlib.integrations.base_client.errors import OAuthError  # type: ignore[import-untyped]
from authlib.integrations.starlette_client import OAuth  # type: ignore[import-untyped]
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.config import get_settings
from app.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
oauth = OAuth()
oauth.register(
    "matrix",
    client_id=settings.matrix_oidc_client_id,
    client_secret=settings.matrix_oidc_client_secret,
    server_metadata_url=(
        f"{settings.matrix_oidc_issuer.rstrip('/')}/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid",
        "code_challenge_method": "S256",
        "token_endpoint_auth_method": (
            "client_secret_basic" if settings.matrix_oidc_client_secret else "none"
        ),
    },
)


@router.get("/matrix/login")
async def start_matrix_login(request: Request) -> Response:
    if not settings.matrix_oidc_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Matrix login is not configured",
        )

    client = oauth.create_client("matrix")
    assert client is not None
    callback = settings.matrix_oidc_redirect_uri or request.url_for(
        "complete_matrix_login"
    )
    return cast(Response, await client.authorize_redirect(request, callback))


@router.get("/matrix/callback")
async def complete_matrix_login(
    request: Request,
    session: Session = Depends(get_session),
) -> Response:
    client = oauth.create_client("matrix")
    assert client is not None
    try:
        token = await client.authorize_access_token(request)
        subject = token["userinfo"]["sub"]
    except (KeyError, OAuthError):
        query = urlencode({"error": "Matrix login failed. Please try again."})
        return RedirectResponse(
            f"{settings.frontend_origin}/login?{query}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    session_token = auth_service.create_session(
        session,
        issuer=settings.matrix_oidc_issuer,
        subject=subject,
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
