import httpx
from pydantic import BaseModel, ValidationError
from ..errors import MatrixIdentityError


class MatrixIdentity(BaseModel):
    """Identity returned by the Matrix Client-Server ``whoami`` endpoint."""

    user_id: str
    device_id: str | None = None
    is_guest: bool = False  # legacy API, should be False by default via MAS


async def get_matrix_identity(
    homeserver_url: str,
    access_token: str,
) -> MatrixIdentity:
    """Resolve the Matrix user associated with an access token."""
    url = f"{homeserver_url.rstrip('/')}/" "_matrix/client/v3/account/whoami"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise MatrixIdentityError("Could not resolve Matrix identity") from exc

    try:
        return MatrixIdentity.model_validate(response.json())
    except (ValueError, ValidationError) as exc:
        raise MatrixIdentityError("Homeserver returned an invalid identity") from exc
