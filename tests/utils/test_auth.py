from __future__ import annotations

from typing import Any

import pytest

from canvas import CanvasAuth, CanvasScope


@pytest.mark.parametrize(
    "auths,expected",
    [
        (
            CanvasAuth("test1", "test2", "test3"),
            {
                "client_id": "test1",
                "client_secret": "test2",
                "canvas_domain": "test3",
                "redirect_uri": "http://localhost:8000/callback",
                "scopes": CanvasScope.NONE,
                "_base_url": "https://test3",
            },
        ),
        (
            CanvasAuth(
                "a1",
                "b2",
                "c3",
                "d4",
                CanvasScope.UPDATE_ACCESS_TOKEN
                | CanvasScope.SHOW_ACCESS_TOKEN,
            ),
            {
                "client_id": "a1",
                "client_secret": "b2",
                "canvas_domain": "c3",
                "redirect_uri": "d4",
                "scopes": CanvasScope.UPDATE_ACCESS_TOKEN
                | CanvasScope.SHOW_ACCESS_TOKEN,
                "_base_url": "https://c3",
            },
        ),
    ],
)
def test_init(auths: CanvasAuth, expected: dict[str, Any]) -> None:
    """Test auth initialization."""
    for key, val in expected.items():
        assert getattr(auths, key) == val


@pytest.mark.parametrize(
    "auths,expected",
    [
        (
            CanvasAuth("test1", "test2", "test3"),
            "https://test3/login/oauth2/auth?client_id=test1&response_type=code"
            "&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback&state={}&scope=",
        ),
        (
            CanvasAuth(
                "a1",
                "b2",
                "c3",
                "d4",
                CanvasScope.UPDATE_ACCESS_TOKEN
                | CanvasScope.SHOW_ACCESS_TOKEN,
            ),
            "https://c3/login/oauth2/auth?client_id=a1&response_type=code"
            "&redirect_uri=d4&state={}&scope=url%3AGET%7C%2Fapi%2Fv1%2Fusers"
            "%2F%3Auser_id%2Ftokens%2F%3Aid+url%3APUT%7C%2Fapi%2Fv1%2Fusers"
            "%2F%3Auser_id%2Ftokens%2F%3Aid",
        ),
    ],
)
def test_auth_url(auths: CanvasAuth, expected: str) -> None:
    """Test auth url."""
    assert auths._get_auth_url() == expected.format(auths._state)  # fmt: skip  # pyright: ignore[reportPrivateUsage]
