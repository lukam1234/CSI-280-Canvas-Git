"""Errors used by Canvas Git
============================

This module contains the errors used by Canvas Git.
All errors should inherit from the base class :class:`CanvasError`.

Example
-------
.. code-block:: python

    raise CanvasError("This is an error message.")
"""

from __future__ import annotations

from typing import Any

__all__ = ("CanvasError", "AuthenticationError", "APIError", "AttributeError")


class CanvasError(Exception):
    """Base class for all errors raised by Canvas Git."""


class AuthenticationError(CanvasError):
    """Raised when authentication with Canvas Git fails."""


class APIError(CanvasError):
    """Raised when an API call fails.

    :param message: The error message.
    :type message: str

    :param status: HTTP status code from the response.
    :type status: int

    :param response: Complete API response body.
    :type response: dict[str, Any]

    :ivar status_code: HTTP status code from the response.
    :vartype status_code: int

    :ivar response: Complete API response body.
    :vartype response: dict[str, Any]

    :ivar message: The error message.
    :vartype message: str

    :raises CanvasError: Base Canvas error class.
    """

    def __init__(
        self, message: str, status: int, response: dict[str, Any]
    ) -> None:
        """Initialize the APIError.

        :param message: The error message.
        :type message: str

        :param status: HTTP status code from the response.
        :type status: int

        :param response: Complete API response body.
        :type response: dict[str, Any]
        """
        super().__init__(message)
        self.status_code = status
        self.response = response


class AttributeError(CanvasError):
    """Raised when an attribute error occurs."""
