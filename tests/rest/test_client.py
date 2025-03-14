# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import datetime
from typing import Any
from unittest.mock import AsyncMock

from httpx import Response
import pytest

from canvas import OAuthToken
from canvas.oauth.auth import CanvasAuth
from canvas.rest.client import CanvasAPIClient
from canvas.errors import APIError
from tests.test_utils import MockAsyncClient


@pytest.fixture
def test_auth() -> CanvasAuth:
    """CanvasAuth for testing."""
    auth = CanvasAuth(
        "test_client_id", "test_client_secret", "test_client_domain"
    )
    auth._client = MockAsyncClient()
    return auth


@pytest.fixture
def test_client(test_auth: CanvasAuth) -> CanvasAPIClient:
    """CanvasAPIClient for testing."""
    client = CanvasAPIClient(
        test_auth,
        "/test_api/test_v1",
    )
    client._client = MockAsyncClient()
    return client


@pytest.fixture
def test_token() -> OAuthToken:
    """Standard OAuthToken to test for equality"""
    return OAuthToken(
        access_token="test_access_token",
        token_type="test_token_type",
        expires_at=datetime.datetime.now() + datetime.timedelta(days=5),
        refresh_token="test_refresh_token",
    )


@pytest.mark.parametrize(
    "endpoint,expected",
    [
        ("/tests", "https://test_client_domain/test_api/test_v1/tests"),
        (
            "/tests/1234",
            "https://test_client_domain/test_api/test_v1/tests/1234",
        ),
        (
            "/tests/1234/a",
            "https://test_client_domain/test_api/test_v1/tests/1234/a",
        ),
        ("tests", "https://test_client_domain/test_api/test_v1/tests"),
        (
            "tests/1234",
            "https://test_client_domain/test_api/test_v1/tests/1234",
        ),
        (
            "tests/1234/a",
            "https://test_client_domain/test_api/test_v1/tests/1234/a",
        ),
        ("//tests", "https://test_client_domain/test_api/test_v1/tests"),
        (
            "//tests/1234",
            "https://test_client_domain/test_api/test_v1/tests/1234",
        ),
        (
            "//tests/1234/a",
            "https://test_client_domain/test_api/test_v1/tests/1234/a",
        ),
    ],
)
def test_get_url(
    test_client: CanvasAPIClient, endpoint: str, expected: str
) -> None:
    """Test getting api endpoint url."""
    assert test_client._get_url(endpoint) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response,expected",
    [
        (Response(200, json={"message": "ok"}), {"message": "ok"}),
        (
            Response(202, json={"message": "accepted"}),
            {"message": "accepted"},
        ),
        (
            Response(200, json={"hello": "goodbye", "sun": "moon"}),
            {"hello": "goodbye", "sun": "moon"},
        ),
        (
            Response(200, json={"a": [1, 2, 3], "b": {"a": "b"}}),
            {"a": [1, 2, 3], "b": {"a": "b"}},
        ),
        (
            Response(200, json={"a": [1, 2, 3], "b": {"a": "b"}}),
            {"a": [1, 2, 3], "b": {"a": "b"}},
        ),
        (
            Response(200),
            {},
        ),
    ],
)
async def test_process_response(
    test_client: CanvasAPIClient,
    response: Response,
    expected: dict[str, Any],
) -> None:
    """Test api response processing."""
    assert await test_client._process_response(response) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response,expected",
    [
        (Response(302, json={"message": "redirect"}), "redirect"),
        (Response(404, json={"message": "not found"}), "not found"),
        (Response(403, json={"message": "forbidden", "a": "b"}), "forbidden"),
        (Response(400), "API request failed."),
    ],
)
async def test_process_response_failure(
    test_client: CanvasAPIClient,
    response: Response,
    expected: str,
) -> None:
    """Test api response processing on failure."""
    with pytest.raises(APIError, match=expected):
        await test_client._process_response(response)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,endpoint,mock_response,expected",
    [
        (
            "GET",
            "test",
            Response(200, json={"message": "test"}),
            {"message": "test"},
        ),
        (
            "POST",
            "/test/a",
            Response(202, json={"test": "test"}),
            {"test": "test"},
        ),
        (
            "DELETE",
            "test/a",
            Response(204, json={"test2": "test2"}),
            {"test2": "test2"},
        ),
    ],
)
async def test_request(
    test_client: CanvasAPIClient,
    test_token: OAuthToken,
    method: str,
    endpoint: str,
    mock_response: Response,
    expected: dict[str, Any],
) -> None:
    """Test api requests."""
    test_client.auth._token = test_token
    test_client._client.request = AsyncMock(return_value=mock_response)

    # Test with given method
    assert await test_client._request(method, endpoint) == expected

    # Test with every method
    assert await test_client.get(endpoint) == expected
    assert await test_client.put(endpoint) == expected
    assert await test_client.post(endpoint) == expected
    assert await test_client.delete(endpoint) == expected
