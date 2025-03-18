# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import datetime
from typing import Any

import pytest
from httpx._client import ClientState

from canvas.errors import AuthenticationError
from canvas.utils import CanvasScope
from canvas.oauth import CanvasAuth
from canvas.oauth.types import OAuthCallback, OAuthToken
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
def test_auth_http_error() -> CanvasAuth:
    """CanvasAuth for testing that raises HTTPError."""
    auth = CanvasAuth(
        "test_client_id", "test_client_secret", "test_client_domain"
    )
    auth._client = MockAsyncClient(invalid_response=True)
    return auth


@pytest.fixture
def test_token() -> OAuthToken:
    """Standard OAuthToken to test for equality"""
    return OAuthToken(
        access_token="test_access_token",
        token_type="test_token_type",
        expires_at=datetime.datetime.now() + datetime.timedelta(days=5),
        refresh_token="test_refresh_token",
    )


@pytest.fixture
def test_token_expired() -> OAuthToken:
    """Standard OAuthToken to test for equality"""
    return OAuthToken(
        access_token="test_access_token",
        token_type="test_token_type",
        expires_at=datetime.datetime.now() - datetime.timedelta(days=5),
        refresh_token="test_refresh_token",
    )


@pytest.mark.parametrize(
    "auth,expected",
    [
        (
            CanvasAuth(
                "test_client_id", "test_client_secret", "test_client_domain"
            ),
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "canvas_domain": "test_client_domain",
                "redirect_uri": "http://localhost:8000/callback",
                "scopes": CanvasScope.NONE,
                "_base_url": "https://test_client_domain",
            },
        ),
        (
            CanvasAuth(
                "test_client_id",
                "test_client_secret",
                "test_client_domain",
                "test_redirect_url",
                CanvasScope.UPDATE_ACCESS_TOKEN
                | CanvasScope.SHOW_ACCESS_TOKEN,
            ),
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "canvas_domain": "test_client_domain",
                "redirect_uri": "test_redirect_url",
                "scopes": CanvasScope.UPDATE_ACCESS_TOKEN
                | CanvasScope.SHOW_ACCESS_TOKEN,
                "_base_url": "https://test_client_domain",
            },
        ),
    ],
)
def test_init(auth: CanvasAuth, expected: dict[str, Any]) -> None:
    """Test auth initialization."""
    for key, val in expected.items():
        assert getattr(auth, key) == val


@pytest.mark.parametrize(
    "auth,expected",
    [
        (
            CanvasAuth(
                "test_client_id", "test_client_secret", "test_client_domain"
            ),
            "https://test_client_domain/login/oauth2/auth?client_id=test_client_id&response_type=code"
            "&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback&state={}&scope=",
        ),
        (
            CanvasAuth(
                "test_client_id",
                "test_client_secret",
                "test_client_domain",
                "test_redirect_url",
                CanvasScope.UPDATE_ACCESS_TOKEN
                | CanvasScope.SHOW_ACCESS_TOKEN,
            ),
            "https://test_client_domain/login/oauth2/auth?client_id=test_client_id&response_type=code"
            "&redirect_uri=test_redirect_url&state={}&scope=url%3AGET%7C%2Fapi%2Fv1%2Fusers"
            "%2F%3Auser_id%2Ftokens%2F%3Aid+url%3APUT%7C%2Fapi%2Fv1%2Fusers"
            "%2F%3Auser_id%2Ftokens%2F%3Aid",
        ),
    ],
)
def test_auth_url(auth: CanvasAuth, expected: str) -> None:
    """Test auth url."""
    assert auth._get_auth_url() == expected.format(auth._state)


@pytest.mark.asyncio
async def test_exchange_code(
    test_auth: CanvasAuth, test_token: OAuthToken
) -> None:
    """Test exchange code."""
    await test_auth._exchange_code("test_code")

    assert test_auth._token is not None
    assert test_auth._token.access_token == test_token.access_token
    assert test_auth._token.token_type == test_token.token_type
    assert test_auth._token.refresh_token == test_token.refresh_token


@pytest.mark.asyncio
async def test_exchange_code_http_error(
    test_auth_http_error: CanvasAuth,
) -> None:
    """Test exchange code with http error."""
    with pytest.raises(
        AuthenticationError,
        match=f"Token exchange failed: .*test_error_text.*",
    ):
        await test_auth_http_error._exchange_code("test_code")


@pytest.mark.asyncio
async def test_refresh_token(
    test_auth: CanvasAuth, test_token: OAuthToken
) -> None:
    """Test refresh token."""
    await test_auth._exchange_code("test_code")
    await test_auth._refresh_token()

    assert test_auth._token is not None
    assert test_auth._token.access_token == test_token.access_token
    assert test_auth._token.token_type == test_token.token_type
    assert test_auth._token.refresh_token == test_token.refresh_token


@pytest.mark.asyncio
async def test_refresh_token_no_token(test_auth: CanvasAuth) -> None:
    """Test refresh token without token."""
    with pytest.raises(
        AuthenticationError, match="No refresh token available"
    ):
        await test_auth._refresh_token()


@pytest.mark.asyncio
async def test_refresh_token_http_error(
    test_auth_http_error: CanvasAuth, test_token: OAuthToken
) -> None:
    """Test refresh token with http error."""
    test_auth_http_error._token = test_token
    with pytest.raises(
        AuthenticationError, match=f"Token refresh failed: .*test_error_text.*"
    ):
        await test_auth_http_error._refresh_token()


@pytest.mark.asyncio
async def test_handle_callback(
    test_auth: CanvasAuth, test_token: OAuthToken
) -> None:
    """Test handle callback."""
    test_callback = OAuthCallback(code="test_code", state=test_auth._state)
    await test_auth._handle_callback(test_callback)

    assert test_auth._token is not None
    assert test_auth._token.access_token == test_token.access_token
    assert test_auth._token.token_type == test_token.token_type
    assert test_auth._token.refresh_token == test_token.refresh_token


@pytest.mark.asyncio
async def test_invalid_handle_callback(test_auth: CanvasAuth) -> None:
    """Test handle callback with invalid state."""
    test_callback = OAuthCallback(code="test_code", state="test_invalid_state")
    with pytest.raises(
        AuthenticationError,
        match="OAuth2 state parameter mismatch, possible CSRF attack?",
    ):
        await test_auth._handle_callback(test_callback)


@pytest.mark.asyncio
async def test_close(test_auth: CanvasAuth) -> None:
    """Test close client."""
    await test_auth.close()
    assert test_auth._client._state == ClientState.CLOSED


def test_authorized(test_auth: CanvasAuth, test_token: OAuthToken) -> None:
    """Test authorization."""
    test_auth._token = test_token
    assert test_auth.authorized


def test_authorized_no_token(test_auth: CanvasAuth) -> None:
    """Test authorization without token."""
    assert not test_auth.authorized


def test_authorized_expired(
    test_auth: CanvasAuth, test_token_expired: OAuthToken
) -> None:
    """Test authorization with expired token."""
    test_auth._token = test_token_expired
    assert not test_auth.authorized


@pytest.mark.asyncio
async def test_fetch_token(test_auth: CanvasAuth, test_token) -> None:
    """Test fetch token."""
    test_auth._token = test_token
    assert await test_auth.fetch_token() == "test_access_token"


@pytest.mark.asyncio
async def test_fetch_token_no_token(test_auth: CanvasAuth) -> None:
    """Test fetch token without token."""
    with pytest.raises(
        AuthenticationError,
        match=r"No token available, call authenticate\(\) first",
    ):
        await test_auth.fetch_token()


@pytest.mark.asyncio
async def test_fetch_token_expired(
    test_auth: CanvasAuth, test_token_expired: OAuthToken
) -> None:
    """Test fetch token with expired token."""
    test_auth._token = test_token_expired
    assert await test_auth.fetch_token() == "test_access_token"
