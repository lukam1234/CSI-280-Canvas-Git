"""Canvas OAuth types.
======================

Type definitions and data models for Canvas OAuth flow.
"""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict

from attrs import define, field

__all__ = ("TokenResponse", "OAuthCallback", "OAuthToken")


class TokenResponse(TypedDict):
    """Response from token endpoint."""

    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int


class OAuthCallback(TypedDict):
    """OAuth callback data."""

    code: str
    state: str


@define(frozen=True, slots=True)
class OAuthToken:
    """OAuth token information."""

    access_token: str = field()
    refresh_token: str = field()
    expires_at: datetime = field()
    token_type: str = field(default="Bearer")

    @property
    def auth_header(self) -> str:
        """Get authorization header value."""
        return f"{self.token_type} {self.access_token}"

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now() > self.expires_at
