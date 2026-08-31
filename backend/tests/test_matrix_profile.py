import asyncio

import httpx
import pytest

from app.services.auth.matrix_profile import get_matrix_profile


def test_get_matrix_profile__uses_verified_encoded_user_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_url = (
        "https://matrix.example.com/_matrix/client/v3/profile/"
        "%40penguinboi%3Amatrix.org"
    )
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
                    "displayname": "Penguin Boi",
                    "avatar_url": "mxc://matrix.org/avatar",
                },
                request=httpx.Request("GET", url),
            )

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    profile = asyncio.run(
        get_matrix_profile(
            "https://matrix.example.com/",
            "@penguinboi:matrix.org",
        )
    )

    assert profile.displayname == "Penguin Boi"
    assert profile.avatar_url == "mxc://matrix.org/avatar"
    assert request_headers == {"Accept": "application/json"}
