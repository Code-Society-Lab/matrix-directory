import asyncio

import pytest

from app.services.matrix_oauth import refresh_matrix_access_token


def test_refresh_matrix_access_token__returns_rotated_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        async def fetch_access_token(self, **kwargs: str) -> dict[str, str]:
            assert kwargs == {
                "grant_type": "refresh_token",
                "refresh_token": "existing-refresh-token",
            }
            return {
                "access_token": "fresh-access-token",
                "refresh_token": "rotated-refresh-token",
            }

    monkeypatch.setattr(
        "app.services.matrix_oauth.get_matrix_oauth_client",
        lambda: FakeClient(),
    )

    token = asyncio.run(refresh_matrix_access_token("existing-refresh-token"))

    assert token.access_token == "fresh-access-token"
    assert token.refresh_token == "rotated-refresh-token"
