from collections.abc import AsyncIterator
from dataclasses import dataclass
from urllib.parse import quote, unquote, urlsplit

import httpx

from .errors import MatrixMediaError

THUMBNAIL_SIZE = 128
MAX_THUMBNAIL_BYTES = 2 * 1024 * 1024

# SVG is deliberately excluded: it is script-capable, and this proxy serves
# homeserver bytes from the application's own origin.
ALLOWED_MEDIA_TYPES = frozenset(
    {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif",
    }
)


@dataclass
class MatrixMediaStream:
    """Open HTTP resources for a streaming Matrix media response."""

    client: httpx.AsyncClient
    response: httpx.Response
    media_type: str

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Yield the response body, stopping if it exceeds the size budget."""
        streamed = 0
        async for chunk in self.response.aiter_bytes():
            streamed += len(chunk)
            if streamed > MAX_THUMBNAIL_BYTES:
                return

            yield chunk

    async def close(self) -> None:
        await self.response.aclose()
        await self.client.aclose()


def matrix_thumbnail_url(*, mxc_uri: str, homeserver_url: str) -> str:
    """Build the authenticated v1 thumbnail URL for a Matrix Content URI."""
    parsed = urlsplit(mxc_uri)
    media_id = unquote(parsed.path.removeprefix("/"))
    if (
        parsed.scheme != "mxc"
        or not parsed.netloc
        or not media_id
        or "/" in media_id
        or parsed.query
        or parsed.fragment
    ):
        raise MatrixMediaError("Invalid Matrix Content URI")

    return (
        f"{homeserver_url.rstrip('/')}"
        "/_matrix/client/v1/media/thumbnail/"
        f"{quote(parsed.netloc, safe='')}/{quote(media_id, safe='')}"
        f"?width={THUMBNAIL_SIZE}&height={THUMBNAIL_SIZE}"
        "&method=crop&animated=false"
    )


def _resolve_media_type(response: httpx.Response) -> str:
    """Return the response media type, rejecting anything not an allowed image."""
    header = str(response.headers.get("content-type", ""))
    media_type = header.split(";")[0].strip().lower()
    if media_type not in ALLOWED_MEDIA_TYPES:
        raise MatrixMediaError(f"Homeserver returned unsupported media: {media_type!r}")

    declared_length = response.headers.get("content-length")
    if declared_length is not None:
        try:
            if int(declared_length) > MAX_THUMBNAIL_BYTES:
                raise MatrixMediaError("Homeserver returned oversized media")
        except ValueError as exc:
            raise MatrixMediaError(
                "Homeserver returned an invalid content length"
            ) from exc

    return media_type


async def open_matrix_thumbnail_stream(
    *,
    homeserver_url: str,
    access_token: str,
    mxc_uri: str,
) -> MatrixMediaStream:
    """Open an authenticated Matrix thumbnail stream without buffering it.

    Redirects are not followed: the response would otherwise come from a host
    this application never validated, which turns a homeserver into a
    server-side request forgery primitive.
    """
    client = httpx.AsyncClient(timeout=10.0, follow_redirects=False)
    try:
        response = await client.send(
            client.build_request(
                "GET",
                matrix_thumbnail_url(
                    mxc_uri=mxc_uri,
                    homeserver_url=homeserver_url,
                ),
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": ", ".join(sorted(ALLOWED_MEDIA_TYPES)),
                },
            ),
            stream=True,
        )
        response.raise_for_status()
        return MatrixMediaStream(
            client=client,
            response=response,
            media_type=_resolve_media_type(response),
        )
    except (httpx.HTTPError, MatrixMediaError):
        await client.aclose()
        raise
