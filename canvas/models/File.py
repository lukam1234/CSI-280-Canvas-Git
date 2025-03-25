from __future__ import annotations

from typing import Any

from attrs import define, field

from ..rest import CanvasAPIClient

from base import Model

@define
class FileModel(Model):
    """Represents a file object in the Canvas API."""

    id: int = field()
    uuid: str = field()
    folder_id: int = field()
    display_name: str = field()
    filename: str = field()
    content_type: str = field()
    url: str = field()
    size: int = field()
    created_at: str = field()
    updated_at: str = field()
    unlock_at: str = field()
    locked: bool = field()
    hidden: bool = field()
    lock_at: str = field()
    hidden_for_user: bool = field()
    visibility_level: str = field()
    thumbnail_url: str = field()
    modified_at: str = field()
    mime_class: str = field()
    media_entry_id: str = field()
    locked_for_user: bool = field()
    lock_info: dict[str, Any] = field()
    lock_explanation: str = field()
    preview_url: str = field()

    @classmethod
    def from_json(
        cls, client: CanvasAPIClient, data: dict[str, Any]
    ) -> FileModel:
        """Create a FileModel instance from JSON data."""
        return super().from_json(client, data)