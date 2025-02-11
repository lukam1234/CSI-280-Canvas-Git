"""Canvas LMS OAuth2 Scopes
===========================

This module implements scope management for Canvas LMS OAuth2 authentication.
It provides a flag-based system for managing API permissions.

Example
-------
.. code-block:: python

    scopes = {CanvasScope.SHOW_ACCESS_TOKEN, CanvasScope.USER_INFO}
    scope_str = CanvasScope.combine_scopes(scopes)
"""

from __future__ import annotations

from enum import Flag, auto

__all__ = ("CanvasScope",)


class CanvasScope(Flag):
    """OAuth2 scopes for Canvas LMS API access.

    :ivar NONE: No scopes.

    :ivar SHOW_ACCESS_TOKEN: Read access tokens for the authenticated user.
    :ivar CREATE_ACCESS_TOKEN: Create access tokens for the authenticated user.
    :ivar UPDATE_ACCESS_TOKEN: Update access tokens for the authenticated user.
    :ivar DELETE_ACCESS_TOKEN: Delete access tokens for the authenticated user.

    :ivar USER_INFO: Read user information for the authenticated user.
    """

    # TODO: Add more scopes.
    NONE = auto()

    # OAuth2 scopes for Canvas LMS API.
    SHOW_ACCESS_TOKEN = auto()
    CREATE_ACCESS_TOKEN = auto()
    UPDATE_ACCESS_TOKEN = auto()
    DELETE_ACCESS_TOKEN = auto()

    USER_INFO = auto()

    @classmethod
    def from_string(cls, scope: str) -> CanvasScope:
        """Convert a string scope to CanvasScope flag.

        :param scope: String representation of scope.
        :type scope: str

        :return: Corresponding CanvasScope flag.
        :rtype: CanvasScope

        :raises ValueError: If scope string is invalid.
        """
        try:
            return cls[scope.upper()]
        except KeyError:
            raise ValueError(f"Invalid scope: {scope}.")

    def to_str(self) -> str:
        """Convert flag to Canvas LMS scope string.

        :return: Canvas LMS formatted scope string.
        :rtype: str
        """
        # flake8: noqa
        scope_map = {
            CanvasScope.NONE: "",
            CanvasScope.SHOW_ACCESS_TOKEN: "url:GET|/api/v1/users/:user_id/tokens/:id",
            CanvasScope.CREATE_ACCESS_TOKEN: "url:POST|/api/v1/users/:user_id/tokens",
            CanvasScope.UPDATE_ACCESS_TOKEN: "url:PUT|/api/v1/users/:user_id/tokens/:id",
            CanvasScope.DELETE_ACCESS_TOKEN: "url:DELETE|/api/v1/users/:user_id/tokens/:id",
            CanvasScope.USER_INFO: "/auth/userinfo",
        }

        return scope_map.get(self, "")

    @staticmethod
    def combine_scopes(scopes: set[CanvasScope]) -> str:
        """Combine multiple scope flags into a Canvas scope string.

        :param scopes: Set of CanvasScope flags.
        :type scopes: set[CanvasScope]

        :return: Combined scope string for Canvas LMS.
        :rtype: str
        """
        return " ".join(scope.to_str() for scope in scopes)
