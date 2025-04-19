"""Canvas LMS OAuth2 Scopes
===========================

This module implements scope management for Canvas LMS OAuth2 authentication.
It provides a flag-based system for managing API permissions.

Example
-------
.. code-block:: python

    required_scopes = (
        CanvasScope.SHOW_ACCESS_TOKEN |
        CanvasScope.USER_INFO
    )
"""

from __future__ import annotations

from enum import Flag, auto

__all__ = ("CanvasScope",)


class CanvasScope(Flag):
    """OAuth2 scopes for Canvas LMS API access.

    :ivar NONE: No scopes.
    :ivar USER_INFO: Read user information for the authenticated user.
    :ivar SHOW_ACCESS_TOKEN: Read access tokens for the authenticated user.
    :ivar CREATE_ACCESS_TOKEN: Create access tokens for the authenticated user.
    :ivar UPDATE_ACCESS_TOKEN: Update access tokens for the authenticated user.
    :ivar DELETE_ACCESS_TOKEN: Delete access tokens for the authenticated user.
    """

    # Base scopes.
    NONE = 0

    # User information scopes.
    USER_INFO = auto()

    # Token management scopes.
    SHOW_ACCESS_TOKEN = auto()
    CREATE_ACCESS_TOKEN = auto()
    UPDATE_ACCESS_TOKEN = auto()
    DELETE_ACCESS_TOKEN = auto()
    UPLOAD_SUBMISSION_FILE = auto()

    @classmethod
    def from_str(cls, scope_str: str) -> CanvasScope:
        """Convert a string scope to CanvasScope flag.

        :param scope_str: String representation of scope.
        :type scope_str: str

        :return: Corresponding CanvasScope flag.
        :rtype: CanvasScope

        :raises ValueError: If scope string is invalid.
        """
        try:
            return cls[scope_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid scope identifier: {scope_str}.")

    def __str__(self) -> str:
        """Convert CanvasScope flag to string.

        :return: String representation of CanvasScope flag.
        :rtype: str
        """
        # flake8: noqa
        _SCOPE_MAPPING = {
            CanvasScope.USER_INFO: "/auth/userinfo",
            CanvasScope.SHOW_ACCESS_TOKEN: "url:GET|/api/v1/users/:user_id/tokens/:id",
            CanvasScope.CREATE_ACCESS_TOKEN: "url:POST|/api/v1/users/:user_id/tokens",
            CanvasScope.UPDATE_ACCESS_TOKEN: "url:PUT|/api/v1/users/:user_id/tokens/:id",
            CanvasScope.DELETE_ACCESS_TOKEN: "url:DELETE|/api/v1/users/:user_id/tokens/:id",
            CanvasScope.UPLOAD_SUBMISSION_FILE: "url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/files",
        }

        if self == CanvasScope.NONE:
            return ""

        scopes: list[str] = []
        for scope in CanvasScope:
            if self & scope:
                if pattern := _SCOPE_MAPPING.get(scope):
                    scopes.append(pattern)

        return " ".join(scopes)
