# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import pytest

from canvas.oauth.auth import CanvasAuth
from canvas.rest.client import CanvasAPIClient
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
    assert test_client._get_url(endpoint) == expected
