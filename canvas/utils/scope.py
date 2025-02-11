"""Canvas LMS OAuth2 Scopes
===========================

This module implements scope management for Canvas LMS OAuth2 authentication.
It provides a flag-based system for managing API permissions.

Example
-------
.. code-block:: python

   auth = CanvasAuth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        redirect_uri="http://localhost:8000/callback",
        canvas_domain="YOUR_CANVAS_DOMAIN"
        scopes=CanvasScope.USER_INFO | ...
    )
"""

from __future__ import annotations

from enum import Flag, auto

__all__ = ("CanvasScope",)


class CanvasScope(Flag):
    """OAuth2 scopes for Canvas LMS API access.

    :ivar: USER_INFO: Read user information for the authenticated user.
    """

    # TODO: Add more scopes.
    USER_INFO = auto()

    @classmethod
    def from_string(cls, scope: str) -> CanvasScope:
        """Convert a string scope to CanvasScope flag..

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
        scope_map = {
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
