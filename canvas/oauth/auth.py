"""Canvas LMS API OAuth2 client.
================================

Implements an async client for OAuth2 authentication with Canvas LMS API.

Example
-------
.. code-block:: python

    auth = CanvasAuth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        redirect_uri="http://localhost:8000/callback",
        canvas_domain="YOUR_CANVAS_DOMAIN",
        scopes=CanvasScope.USER_INFO, # Requested scopes.
    )

    await auth.authenticate()  # Starts OAuth flow.
"""

from __future__ import annotations

import webbrowser
from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Any, cast
from urllib.parse import urlencode

from attrs import define, field
from httpx import AsyncClient, HTTPError

from ..errors import AuthenticationError
from ..utils import CanvasScope
from .server import create_server
from .types import OAuthCallback, OAuthToken, TokenResponse

__all__ = ("CanvasAuth",)


@define
class CanvasAuth:
    """Handles OAuth2 authentication flow for Canvas LMS API.

    :param client_id: OAuth2 client ID from Canvas LMS.
    :type client_id: str

    :param client_secret: OAuth2 client secret from Canvas LMS.
    :type client_secret: str

    :param canvas_domain: Canvas LMS instance domain.
    :type canvas_domain: str

    :param redirect_uri: OAuth2 callback URL registered with Canvas.
    :type redirect_uri: str

    :param scopes: Requested API scopes.
    :type scopes: :class:`CanvasScope`

    :ivar client_id: OAuth2 client ID from Canvas LMS.
    :vartype client_id: str

    :ivar client_secret: OAuth2 client secret from Canvas LMS.
    :vartype client_secret: str

    :ivar canvas_domain: Canvas LMS instance domain.
    :vartype canvas_domain: str

    :ivar redirect_uri: OAuth2 callback URL registered with Canvas.
    :vartype redirect_uri: str

    :ivar scopes: Requested API scopes.
    :vartype scopes: :class:`CanvasScope`
    """

    client_id: str = field()
    client_secret: str = field()
    canvas_domain: str = field()
    redirect_uri: str = field(default="http://localhost:8000/callback")
    scopes: CanvasScope = field(default=CanvasScope.NONE)

    _base_url: str = field(init=False)
    _state: str = field(init=False)
    _token: None | OAuthToken = field(init=False, default=None)
    _client: AsyncClient = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._base_url = f"https://{self.canvas_domain}"
        self._state = token_urlsafe(32)
        self._client = AsyncClient()

    async def __aenter__(self) -> CanvasAuth:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def _get_auth_url(self) -> str:
        """Get the URL for the OAuth2 authentication flow.

        :return: Authorization URL for Canvas OAuth.
        :rtype: str
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": self._state,
            "scope": self.scopes,
        }

        return f"{self._base_url}/login/oauth2/auth?{urlencode(params)}"

    async def _handle_callback(self, callback: OAuthCallback) -> None:
        """Process OAuth callback data.

        :param callback: The callback data received.
        :type callback: :class:`OAuthCallback`

        :raises AuthenticationError: If state verification fails.
        """
        if callback["state"] != self._state:
            raise AuthenticationError(
                "OAuth2 state parameter mismatch, possible CSRF attack?"
            )

        await self._exchange_code(callback["code"])

    async def _exchange_code(self, code: str) -> None:
        """Exchange authorization code for access token.

        :param code: Authorization code from callback.
        :type code: str

        :raises AuthenticationError: If token exchange fails.
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/login/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code,
                },
            )

            response.raise_for_status()
            data = cast(TokenResponse, response.json())

            expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
            self._token = OAuthToken(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=expires_at,
                token_type=data["token_type"],
            )

        except HTTPError as e:
            raise AuthenticationError(f"Token exchange failed: {str(e)}")

    async def _refresh_token(self) -> None:
        """Refresh the access token using the refresh token.

        :raises AuthenticationError: If token refresh fails.
        """
        if not self._token:
            raise AuthenticationError("No refresh token available")

        try:
            response = await self._client.post(
                f"{self._base_url}/login/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self._token.refresh_token,
                },
            )

            response.raise_for_status()
            data = cast(TokenResponse, response.json())

            expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
            self._token = OAuthToken(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=expires_at,
                token_type=data["token_type"],
            )

        except HTTPError as e:
            self._token = None  # Clear invalid token.
            raise AuthenticationError(f"Token refresh failed: {str(e)}")

    async def authenticate(self) -> None:
        """Start the OAuth2 authentication flow.

        1. Generate and open the authorization URL in a browser.
        2. Start a local server to receive the callback.
        3. Exchange the auth code for tokens.

        :raises AuthenticationError: If authentication fails.
        """
        auth_url = self._get_auth_url()
        server = create_server(self._handle_callback)

        # Open browser for auth.
        if not webbrowser.open(auth_url):
            print(f"URL to authenticate: {auth_url}")

        # Wait for callback.
        await server.start()

    async def fetch_token(self) -> str:
        """Fetch the current access token, refreshing if needed.

        :return: The current access token.
        :rtype: str

        :raises AuthenticationError: If no token is available.
        """
        if not self._token:
            raise AuthenticationError(
                "No token available, call authenticate() first"
            )

        if self._token.is_expired:
            await self._refresh_token()

        assert self._token is not None
        return self._token.access_token

    @property
    def authorized(self) -> bool:
        """Check if we have a valid token.

        :return: True if we have a non-expired token.
        :rtype: bool
        """
        return bool(self._token and not self._token.is_expired)

    async def close(self) -> None:
        """Clean up resources."""
        await self._client.aclose()
