"""Canvas LMS OAuth2 server.
============================

Implements a minimal async server for handling-
OAuth2 authentication callbacks.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine
from urllib.parse import parse_qs, urlparse

from .types import OAuthCallback

__all__ = ("OAuthServer", "create_server")


class OAuthCallbackProtocol(asyncio.Protocol):
    """Protocol for handling OAuth callback requests.

    :ivar handler: Handler for successful auth callbacks.
    :vartype handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]

    :ivar event: Event to signal callback completion.
    :vartype event: :class:`asyncio.Event`

    :ivar transport: The current transport.
    :vartype transport: :class:`asyncio.BaseTransport`
    """

    def __init__(
        self,
        handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]],
        event: asyncio.Event,
    ) -> None:
        """Initialize the protocol.

        :param handler: Handler for successful auth callbacks.
        :type handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]

        :param event: Event to signal callback completion.
        :type event: :class:`asyncio.Event`
        """
        self.handler = handler
        self.event = event
        self.transport = None
        self._buffer = ""

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when connection is established.

        :param transport: The current transport.
        :type transport: :class:`asyncio.BaseTransport`
        """
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        """Handle received HTTP request data.

        :param data: Received data.
        :type data: bytes
        """
        request = data.decode()

        # Parse the request.
        try:
            request_line = request.split("\r\n")[0]
            method, path, _ = request_line.split(" ")

            if method == "GET" and path.startswith("/callback"):
                # Parse URL and get query parameters.
                url = urlparse(path)
                params = parse_qs(url.query)

                code = params.get("code", [None])[0]
                state = params.get("state", [None])[0]

                if code and state:
                    callback_data = OAuthCallback(code=code, state=state)
                    asyncio.create_task(self._handle_callback(callback_data))

                    # Send success response.
                    self._send_response(
                        200,
                        "Authorization Successful",
                        "<h1>Authorization Successful</h1>",
                    )
                else:
                    self._send_response(
                        400,
                        "Bad Request",
                        "<h1>Authorization Failed</h1>",
                    )
            else:
                # Send 404 for non-callback requests.
                self._send_response(404, "Not Found", "<h1>404 Not Found</h1>")

        except Exception:
            self._send_response(
                500, "Internal Server Error", "<h1>Internal Server Error</h1>"
            )

    def _send_response(self, status: int, status_text: str, body: str) -> None:
        """Send an HTTP response.

        :param status: HTTP status code.
        :type status: int

        :param status_text: Status text.
        :type status_text: str

        :param body: Response body HTML.
        :type body: str
        """
        assert self.transport is not None

        html = f"""
        <html>
            <body>
                {body}
            </body>
        </html>
        """

        response = (
            f"HTTP/1.1 {status} {status_text}\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(html)}\r\n"
            "\r\n"
            f"{html}"
        )

        self.transport.write(response.encode())  # type: ignore
        self.transport.close()

    async def _handle_callback(self, data: OAuthCallback) -> None:
        """Process the OAuth callback data.

        :param data: The callback data to process.
        :type data: OAuthCallback
        """
        await self.handler(data)
        self.event.set()


class OAuthServer:
    """Async OAuth callback server implementation.

    :ivar handler: Handler for successful auth callbacks.
    :vartype handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]

    :ivar host: Server host address.
    :vartype host: str

    :ivar port: Server port.
    :vartype port: int
    """

    def __init__(
        self,
        handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]],
        host: str = "localhost",
        port: int = 8000,
    ) -> None:
        """Initialize the OAuth server.

        :param handler: Async function to handle successful auth.
        :type handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]

        :param host: Server host address, defaults to "localhost".
        :type host: str

        :param port: Server port, defaults to 8000.
        :type port: int
        """
        self.handler = handler
        self.host = host
        self.port = port

        self._event = asyncio.Event()
        self._server = None

    async def start(self) -> None:
        """Start the OAuth callback server."""
        try:
            loop = asyncio.get_running_loop()

            # Create server
            self._server = await loop.create_server(
                lambda: OAuthCallbackProtocol(self.handler, self._event),
                self.host,
                self.port,
            )

            # Wait for callback completion
            await self._event.wait()

        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up server resources."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()


def create_server(
    handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]],
    host: str = "localhost",
    port: int = 8000,
) -> OAuthServer:
    """Create a new OAuth callback server.

    :param handler: Async function to handle successful auth.
    :type handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]

    :param host: Server host address, defaults to "localhost".
    :type host: str

    :param port: Server port, defaults to 8000.
    :type port: int

    :return: Configured OAuth server instance.
    :rtype: OAuthServer
    """
    return OAuthServer(handler, host, port)
