from typing import Any, Protocol, cast

from authlib.integrations.base_client.errors import OAuthError  # type: ignore[import-untyped]
from authlib.integrations.starlette_client import OAuth  # type: ignore[import-untyped]
from pydantic import BaseModel, ValidationError

from app.config import get_settings

from .errors import MatrixOAuthTokenError

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
        "scope": settings.matrix_oidc_scope,
        "code_challenge_method": "S256",
        "token_endpoint_auth_method": (
            "client_secret_basic" if settings.matrix_oidc_client_secret else "none"
        ),
    },
)


class MatrixOAuthClient(Protocol):
    """The subset of the authlib client this application depends on."""

    async def authorize_redirect(self, request: Any, redirect_uri: Any) -> Any: ...

    async def authorize_access_token(self, request: Any) -> dict[str, Any]: ...

    async def fetch_access_token(self, **kwargs: Any) -> dict[str, Any]: ...


class MatrixOAuthToken(BaseModel):
    """OAuth token data needed by the Matrix media proxy."""

    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None


def get_matrix_oauth_client() -> MatrixOAuthClient:
    """Return the configured Matrix OAuth client."""
    client = oauth.create_client("matrix")
    if client is None:
        raise MatrixOAuthTokenError("Matrix OAuth client is not registered")

    return cast(MatrixOAuthClient, client)


async def refresh_matrix_access_token(refresh_token: str) -> MatrixOAuthToken:
    """Exchange an encrypted credential's refresh token for an access token."""
    client = get_matrix_oauth_client()
    try:
        token = await client.fetch_access_token(
            grant_type="refresh_token",
            refresh_token=refresh_token,
        )
        return MatrixOAuthToken.model_validate(token)
    except (KeyError, OAuthError, ValidationError, ValueError) as exc:
        raise MatrixOAuthTokenError("Could not refresh Matrix access token") from exc
