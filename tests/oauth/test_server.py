# These really aren't great tests but it's so hard writing tests for something
# I didn't write myself.

# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine
from unittest.mock import AsyncMock, Mock
from urllib.parse import urlencode

import pytest

from canvas.oauth import OAuthServer, OAuthCallback, create_server
from canvas.oauth.server import OAuthCallbackProtocol


@pytest.fixture
def mock_callback_handler() -> (
    Callable[[OAuthCallback], Coroutine[Any, Any, None]]
):
    def handler(_: OAuthCallback) -> Coroutine[Any, Any, None]:
        return Coroutine[Any, Any, None]()

    return handler


@pytest.fixture
def mock_callback_protocol(
    mock_callback_handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]
) -> OAuthCallbackProtocol:
    return OAuthCallbackProtocol(mock_callback_handler, asyncio.Event())


def test_create_server(
    mock_callback_handler: Callable[[OAuthCallback], Coroutine[Any, Any, None]]
) -> None:
    server = create_server(mock_callback_handler, "test_host", 1234)

    assert isinstance(server, OAuthServer)
    assert server.handler == mock_callback_handler
    assert server.host == "test_host"
    assert server.port == 1234


def test_connection_made(mock_callback_protocol: OAuthCallbackProtocol):
    transport = asyncio.Transport()
    mock_callback_protocol.connection_made(transport)
    assert mock_callback_protocol.transport == transport


def test_data_received(mock_callback_protocol: OAuthCallbackProtocol):
    mock_data = b"GET /callback?code=test_code?state=test_state a\r\n"

    mock_callback_protocol.transport = Mock(asyncio.Transport)
    mock_callback_protocol.transport.write = lambda _: None
    mock_callback_protocol.transport.close = lambda: None

    mock_callback_protocol.data_received(mock_data)
