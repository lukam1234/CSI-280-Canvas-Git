from __future__ import annotations

import pytest

from canvas import CanvasScope


def test_single_str() -> None:
    """Test string conversion of single scopes."""
    cases = {
        CanvasScope.NONE: "",
        CanvasScope.USER_INFO: "/auth/userinfo",
        CanvasScope.SHOW_ACCESS_TOKEN: "url:GET|/api/v1/users/:user_id/tokens/:id",
        CanvasScope.CREATE_ACCESS_TOKEN: "url:POST|/api/v1/users/:user_id/tokens",
        CanvasScope.UPDATE_ACCESS_TOKEN: "url:PUT|/api/v1/users/:user_id/tokens/:id",
        CanvasScope.DELETE_ACCESS_TOKEN: "url:DELETE|/api/v1/users/:user_id/tokens/:id",
    }

    for scope, expected in cases.items():
        assert str(scope) == expected


@pytest.mark.parametrize(
    "scopes,expected",
    [
        (
            CanvasScope.SHOW_ACCESS_TOKEN | CanvasScope.USER_INFO,
            "/auth/userinfo url:GET|/api/v1/users/:user_id/tokens/:id",
        ),
        (
            CanvasScope.CREATE_ACCESS_TOKEN | CanvasScope.UPDATE_ACCESS_TOKEN,
            "url:POST|/api/v1/users/:user_id/tokens url:PUT|/api/v1/users/:user_id/tokens/:id",
        ),
    ],
)
def test_multi_str(scopes: CanvasScope, expected: str) -> None:
    """Test string conversion of combined scopes."""
    assert str(scopes) == expected


@pytest.mark.parametrize(
    "scope_str,expected",
    [
        ("USER_INFO", CanvasScope.USER_INFO),
        ("SHOW_ACCESS_TOKEN", CanvasScope.SHOW_ACCESS_TOKEN),
        ("CREATE_ACCESS_TOKEN", CanvasScope.CREATE_ACCESS_TOKEN),
        ("UPDATE_ACCESS_TOKEN", CanvasScope.UPDATE_ACCESS_TOKEN),
        ("DELETE_ACCESS_TOKEN", CanvasScope.DELETE_ACCESS_TOKEN),
        ("NONE", CanvasScope.NONE),
    ],
)
def test_from_str(scope_str: str, expected: CanvasScope) -> None:
    """Test conversion from string to scope for valid inputs."""
    assert CanvasScope.from_str(scope_str) == expected
    assert CanvasScope.from_str(scope_str.lower()) == expected


@pytest.mark.parametrize(
    "invalid_scope",
    [
        "INVALID_SCOPE",
        "READ_COURSES",
        "WRITE_FILES",
        " USER_INFO ",  # Extra whitespace.
        "user info",  # Contains space.
    ],
)
def test_invalid_from_str(invalid_scope: str) -> None:
    """Test conversion from string fails for invalid inputs."""
    with pytest.raises(ValueError, match="Invalid scope identifier"):
        CanvasScope.from_str(invalid_scope)


def test_bitwise_operations() -> None:
    """Test bitwise operations between scopes."""
    combined = CanvasScope.SHOW_ACCESS_TOKEN | CanvasScope.USER_INFO
    assert combined & CanvasScope.SHOW_ACCESS_TOKEN
    assert combined & CanvasScope.USER_INFO
    assert not (combined & CanvasScope.CREATE_ACCESS_TOKEN)
