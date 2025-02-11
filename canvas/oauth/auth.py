"""Canvas LMS API OAuth2 client.
================================

Implements a client for the OAuth2 web flow in order to-
authenticate with the Canvas LMS API.

Example
-------
.. code-block:: python

    auth = CanvasAuth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        redirect_uri="http://localhost:8000/callback",
        canvas_domain="YOUR_CANVAS_DOMAIN",
        scopes="YOUR_SCOPES",
    )

    auth_url = auth.get_auth_url()
"""

from __future__ import annotations

from secrets import token_urlsafe
from typing import TypedDict
from urllib.parse import urlencode

from attrs import define, field
from httpx import AsyncClient, HTTPError

from ..errors import AuthenticationError

__all__ = ("AuthResponse", "CanvasAuth")


class AuthResponse(TypedDict):
    """Authentication response from Canvas LMS API.

    :ivar access_token: The access token used for API requests.
    :vartype access_token: str

    :ivar token_type: The type of token.
    :vartype token_type: str

    :ivar refresh_token: Token used to obtain new access tokens.
    :vartype refresh_token: str

    :ivar expires_in: Number of seconds until token expiration.
    :vartype expires_in: int
    """

    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int


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
    :type scopes: str

    :ivar client_id: OAuth2 client ID from Canvas LMS.
    :vartype client_id: str

    :ivar client_secret: OAuth2 client secret from Canvas LMS.
    :vartype client_secret: str

    :ivar canvas_domain: Canvas LMS instance domain.
    :vartype canvas_domain: str

    :ivar redirect_uri: OAuth2 callback URL registered with Canvas.
    :vartype redirect_uri: str

    :ivar scopes: Requested API scopes.
    :vartype scopes: CanvasScope
    """

    client_id: str = field()
    client_secret: str = field()
    canvas_domain: str = field()
    redirect_uri: str = field(default="http://localhost:8000/callback")
    scopes: str = field(default="")

    _base_url: str = field(init=False)
    _state: None | str = field(default=None, init=False)
    _auth: None | AuthResponse = field(default=None, init=False)

    def __attrs_post_init__(self) -> None:
        self._base_url = f"https://{self.canvas_domain}/"
        self._state = None
        self._auth = None

    def get_auth_url(self) -> str:
        """Get the URL for the OAuth2 authentication flow.
        Note that the only currently supported respone type is "code".

        :return: Authorization URL to redirect users to.
        :rtype: str
        """
        self._state = token_urlsafe(32)  # Stop CSRF attacks.
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": self._state,
            "scope": self.scopes,
        }

        return f"{self._base_url}login/oauth2/auth?{urlencode(params)}"

    async def fetch_token(self) -> str:
        """Fetch the access token for the authenticated user.

        Refreshes the token if it has expired.
        If no tokens are available, an :class:`AuthenticationError` is raised.

        :return: The access token for the authenticated user.
        :raises AuthenticationError: If no tokens are available.
        """
        if not self._auth:
            raise AuthenticationError("No tokens available.")

        # TODO: Add token refreshing after expiration.
        # await ...

        return self._auth["access_token"]

    async def _exchange_code(self, code: str, state: None | str) -> None:
        """Process the callback from the OAuth2 flow.

        :param code: Authorization code from the callback.
        :type code: str

        :param state: State parameter from the callback.
        :type state: str

        :raises AuthenticationError: If the state parameter is mismatched.
        """
        if state and state != self._state:
            raise AuthenticationError("OAuth2 state parameter mismatched.")

        async with AsyncClient() as client:
            try:
                # Attempt to exchange the code for an access token.
                response = await client.post(
                    f"https://{self.canvas_domain}/login/oauth2/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                        "code": code,
                    },
                )

                # Raise an exception if the request failed.
                response.raise_for_status()
                self._auth = response.json()
            except HTTPError as e:
                raise AuthenticationError(f"Token exchange failed: {str(e)}.")

    async def _refresh_token(self) -> None:
        """Refresh the access token using the refresh token.

        :raises AuthenticationError: If no refresh token is available.
        """
        if not self._auth or "refresh_token" not in self._auth:
            raise AuthenticationError("No refresh token available.")

        async with AsyncClient() as client:
            try:
                # Attempt to refresh the access token.
                response = await client.post(
                    f"https://{self.canvas_domain}/login/oauth2/token",
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self._auth["refresh_token"],
                    },
                )

                # Raise an exception if the request failed.
                response.raise_for_status()
                self._auth = response.json()
            except HTTPError as e:
                raise AuthenticationError(f"Token refresh failed: {str(e)}.")
