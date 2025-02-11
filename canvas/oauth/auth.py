"""Canvas LMS API Client with OAuth2 Authentication
===================================================

Implements a client for the OAuth2 web flow for the Canvas LMS API.

Example
-------
.. code-block:: python

    auth = CanvasAuth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        redirect_uri="http://localhost:8000/callback",
        canvas_domain="YOUR_CANVAS_DOMAIN"
    )

    client = CanvasAPIClient(auth)
"""

from __future__ import annotations

from secrets import token_urlsafe
from typing import TypedDict
from urllib.parse import urlencode

from attrs import define, field

from ..utils import CanvasScope

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

    :param redirect_uri: OAuth2 callback URL registered with Canvas.
    :type redirect_uri: str

    :param canvas_domain: Canvas LMS instance domain.
    :type canvas_domain: str

    :ivar client_id: OAuth2 client ID from Canvas LMS.
    :vartype client_id: str

    :ivar client_secret: OAuth2 client secret from Canvas LMS.
    :vartype client_secret: str

    :ivar redirect_uri: OAuth2 callback URL registered with Canvas.
    :vartype redirect_uri: str

    :ivar canvas_domain: Canvas LMS instance domain.
    :vartype canvas_domain: str

    :ivar scopes: Requested API scopes.
    :vartype scopes: CanvasScope
    """

    client_id: str = field()
    client_secret: str = field()
    redirect_uri: str = field()
    canvas_domain: str = field()
    scopes: CanvasScope = field(default=CanvasScope.USER_INFO)

    _base_url: str = field(init=False)
    _state: None | str = field(default=None, init=False)
    _auth: None | AuthResponse = field(default=None, init=False)

    def __attrs_post_init__(self) -> None:
        self._base_url = f"https://{self.canvas_domain}/"

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
            "scope": self.scopes.to_str(),
        }

        return f"{self._base_url}login/oauth2/auth?{urlencode(params)}"
