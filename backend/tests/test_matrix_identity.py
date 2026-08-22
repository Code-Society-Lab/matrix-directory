import asyncio

import httpx
import pytest

from app.services.auth.matrix_identity import get_matrix_identity


def test_get_matrix_identity__sends_bearer_token_to_homeserver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_url = "https://matrix.example.com/_matrix/client/v3/account/whoami"
    request_headers: dict[str, str] = {}

    class FakeAsyncClient:
        def __init__(self, **kwargs: object) -> None:
            assert kwargs == {"timeout": 10.0}

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, url: str, *, headers: dict[str, str]) -> httpx.Response:
            assert url == request_url
            request_headers.update(headers)
            return httpx.Response(
                200,
                json={
                    "user_id": "@penguinboi:matrix.org",
                    "device_id": "MATRIXDIRECTORY",
                    "is_guest": False,
                },
                request=httpx.Request("GET", url),
            )

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    identity = asyncio.run(
        get_matrix_identity("https://matrix.example.com/", "mas-access-token")
    )

    assert identity.user_id == "@penguinboi:matrix.org"
    assert identity.device_id == "MATRIXDIRECTORY"
    assert request_headers == {
        "Authorization": "Bearer mas-access-token",
        "Accept": "application/json",
    }
