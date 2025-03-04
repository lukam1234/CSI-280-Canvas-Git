from __future__ import annotations

from typing import Any

from httpx import HTTPError
from httpx._client import ClientState


class MockAsyncClient:
    """A mock async client for testing."""

    _state = ClientState.CLOSED

    def __init__(
        self, invalid_response: bool = False, expired_token: bool = False
    ) -> None:
        """Initialize the mock async client."""
        self.invalid_response = invalid_response
        self.expired_token = expired_token

    async def post(self, *args, **kwargs) -> MockResponse:
        """Mock post."""
        return MockResponse(self.invalid_response, self.expired_token)

    async def aclose(self) -> None:
        """Mock async close."""
        self._state = ClientState.CLOSED


class MockResponse:
    """A mock OAuth2 response."""

    def __init__(self, invalid: bool, expired: bool):
        """Initialize mock response."""
        self.invalid = invalid
        self.expired = expired

    def raise_for_status(self) -> None:
        """Mock raise for status."""
        if self.invalid:
            raise HTTPError("test_error_text")

    def json(self) -> dict[str, Any]:
        """Mock json data."""
        return {
            "access_token": "test_access_token",
            "token_type": "test_token_type",
            "refresh_token": "test_refresh_token",
            "expires_in": 12345 if not self.expired else -12345,
        }
