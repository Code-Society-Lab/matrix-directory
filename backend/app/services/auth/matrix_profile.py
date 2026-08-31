from urllib.parse import quote

import httpx
from pydantic import BaseModel, ValidationError
from ..errors import MatrixProfileError


class MatrixProfile(BaseModel):
    """Public profile returned by the Matrix Client-Server API."""

    displayname: str | None = None
    avatar_url: str | None = None


async def get_matrix_profile(
    homeserver_url: str,
    user_id: str,
) -> MatrixProfile:
    """Fetch a user's public Matrix profile from the homeserver."""
    encoded_user_id = quote(user_id, safe="")
    url = (
        f"{homeserver_url.rstrip('/')}" f"/_matrix/client/v3/profile/{encoded_user_id}"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise MatrixProfileError("Could not retrieve Matrix profile") from exc

    try:
        return MatrixProfile.model_validate(response.json())
    except (ValueError, ValidationError) as exc:
        raise MatrixProfileError("Homeserver returned an invalid profile") from exc
