"""Canvas LMS OAuth2 server.
============================

Implements a server for handling OAuth2 authentication with Canvas LMS.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

__all__ = (
    "CallbackHandler",
    "CallbackServer",
    "get_auth",
)


class CallbackHandler(BaseHTTPRequestHandler):
    """Request handler for OAuth callbacks."""

    auth_code: None | str = None
    state: None | str = None

    def do_GET(self) -> None:
        """Handle GET requests."""
        query = parse_qs(urlparse(self.path).query)

        self.__class__.auth_code = query.get("code", [None])[0]
        self.__class__.state = query.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        message = "<html><body><h1>Authorization Successful.</h1>"
        self.wfile.write(message.encode())

        # Signal the server to shutdown.
        self.server.auth_received = True  # type: ignore


class CallbackServer(HTTPServer):
    """HTTP server for handling OAuth callbacks.

    :ivar auth_received: If the server has received an OAuth callback.
    :vartype auth_received: bool
    """

    def __init__(
        self, address: tuple[str, int], handler_class: type[CallbackHandler]
    ) -> None:
        """Initialize server with auth_received flag.

        :param address: The server address, (host, port).
        :type server_address: tuple[str, int]

        :param handler_class: Handler class for requests.
        :type handler_class: type
        """
        super().__init__(address, handler_class)
        self.auth_received = False

    def handle_request(self) -> None:
        """Handle a single request and shutdown if auth is received."""
        super().handle_request()

        if self.auth_received:
            self.server_close()


def get_auth() -> tuple[None | str, None | str]:
    """Get authorization code and state from callback.

    :return: The authorization code and state.
    :rtype: tuple[None | str, None | str]
    """
    return CallbackHandler.auth_code, CallbackHandler.state
