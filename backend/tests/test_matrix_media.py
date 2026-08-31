import asyncio
from collections.abc import AsyncIterator, Callable
from typing import ClassVar

import httpx
import pytest

from app.services.errors import MatrixMediaError
from app.services.matrix_media import (
    MAX_THUMBNAIL_BYTES,
    MatrixMediaStream,
    matrix_thumbnail_url,
    open_matrix_thumbnail_stream,
)

THUMBNAIL_URL = (
    "https://matrix.example.com/_matrix/client/v1/media/thumbnail/"
    "matrix.org/avatar?width=128&height=128&method=crop&animated=false"
)


Responder = Callable[[httpx.Request], httpx.Response]


class FakeAsyncClient:
    """Stands in for httpx.AsyncClient so no socket is ever opened."""

    responder: ClassVar[Responder]
    closed: ClassVar[bool] = False
    init_kwargs: ClassVar[dict[str, object]] = {}

    def __init__(self, **kwargs: object) -> None:
        FakeAsyncClient.init_kwargs = kwargs

    def build_request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
    ) -> httpx.Request:
        return httpx.Request(method, url, headers=headers)

    async def send(self, request: httpx.Request, *, stream: bool) -> httpx.Response:
        assert stream is True
        return FakeAsyncClient.responder(request)

    async def aclose(self) -> None:
        FakeAsyncClient.closed = True


def install_fake_client(
    monkeypatch: pytest.MonkeyPatch,
    responder: Responder,
) -> type[FakeAsyncClient]:
    FakeAsyncClient.responder = responder
    FakeAsyncClient.closed = False
    FakeAsyncClient.init_kwargs = {}
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    return FakeAsyncClient


def test_matrix_thumbnail_url__uses_authenticated_v1_endpoint() -> None:
    assert (
        matrix_thumbnail_url(
            mxc_uri="mxc://matrix.org/avatar",
            homeserver_url="https://matrix.example.com/",
        )
        == THUMBNAIL_URL
    )


@pytest.mark.parametrize(
    "mxc_uri",
    [
        "https://matrix.org/avatar.png",
        "mxc://matrix.org/",
        "mxc:///avatar",
        "mxc://matrix.org/nested%2Fpath",
        "mxc://matrix.org/avatar?width=1",
    ],
)
def test_matrix_thumbnail_url__rejects_unusable_uris(mxc_uri: str) -> None:
    with pytest.raises(MatrixMediaError):
        matrix_thumbnail_url(
            mxc_uri=mxc_uri,
            homeserver_url="https://matrix.example.com",
        )


def test_open_matrix_thumbnail_stream__sends_bearer_token_without_redirects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def respond(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers["authorization"]
        seen["url"] = str(request.url)
        return httpx.Response(
            200,
            headers={"content-type": "image/png"},
            content=b"thumbnail",
            request=request,
        )

    client_class = install_fake_client(monkeypatch, respond)

    media = asyncio.run(
        open_matrix_thumbnail_stream(
            homeserver_url="https://matrix.example.com",
            access_token="access-token",
            mxc_uri="mxc://matrix.org/avatar",
        )
    )

    assert seen["authorization"] == "Bearer access-token"
    assert seen["url"] == THUMBNAIL_URL
    assert media.media_type == "image/png"
    assert client_class.init_kwargs["follow_redirects"] is False

    asyncio.run(media.close())
    assert client_class.closed is True


@pytest.mark.parametrize(
    "headers",
    [
        {"content-type": "image/svg+xml"},
        {"content-type": "text/html"},
        {},
        {"content-type": "image/png", "content-length": str(MAX_THUMBNAIL_BYTES + 1)},
    ],
)
def test_open_matrix_thumbnail_stream__rejects_unsafe_or_oversized_media(
    monkeypatch: pytest.MonkeyPatch,
    headers: dict[str, str],
) -> None:
    client_class = install_fake_client(
        monkeypatch,
        lambda request: httpx.Response(
            200,
            headers=headers,
            content=b"payload",
            request=request,
        ),
    )

    with pytest.raises(MatrixMediaError):
        asyncio.run(
            open_matrix_thumbnail_stream(
                homeserver_url="https://matrix.example.com",
                access_token="access-token",
                mxc_uri="mxc://matrix.org/avatar",
            )
        )

    assert client_class.closed is True


def test_open_matrix_thumbnail_stream__does_not_follow_a_redirect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A redirect must fail closed rather than fetch an unvalidated host."""
    client_class = install_fake_client(
        monkeypatch,
        lambda request: httpx.Response(
            302,
            headers={"location": "http://169.254.169.254/latest/meta-data/"},
            request=request,
        ),
    )

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(
            open_matrix_thumbnail_stream(
                homeserver_url="https://matrix.example.com",
                access_token="access-token",
                mxc_uri="mxc://matrix.org/avatar",
            )
        )

    assert client_class.closed is True


def test_iter_bytes__stops_at_the_size_budget() -> None:
    """A response that never declares its length is still capped while streaming."""

    class OversizedStream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for _ in range((MAX_THUMBNAIL_BYTES // 1024) + 8):
                yield b"x" * 1024

    client = httpx.AsyncClient()
    media = MatrixMediaStream(
        client=client,
        response=httpx.Response(
            200,
            headers={"content-type": "image/png"},
            stream=OversizedStream(),
            request=httpx.Request("GET", THUMBNAIL_URL),
        ),
        media_type="image/png",
    )

    async def collect() -> int:
        streamed = sum([len(chunk) async for chunk in media.iter_bytes()])
        await media.close()
        return streamed

    assert asyncio.run(collect()) <= MAX_THUMBNAIL_BYTES
