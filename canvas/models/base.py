"""Canvas base model.
=====================

Implements a base model with serialization and deserialization functionality.
"""

from __future__ import annotations

from typing import Any, TypeVar, cast, get_type_hints

from attrs import asdict, define, field

from ..rest import CanvasAPIClient
from ..errors import AttributeError

T = TypeVar("T", bound="Model")

__all__ = ("Model",)


@define
class Model:
    """Base model class."""

    client: CanvasAPIClient = field()

    @classmethod
    def from_json(
        cls: type[T], client: CanvasAPIClient, data: dict[str, Any]
    ) -> T:
        """Create a model instance from a JSON.

        :param data: JSON data to create the model from.
        :type data: dict[str, Any]

        :return: Model instance created from the JSON data.
        :rtype: T

        :raises AttributeError: If a required field is missing.
        """
        hints = get_type_hints(cls)
        kwargs = {}

        for field_name, field_type in hints.items():
            # TODO: Add optional field support.

            if field_name not in data:
                raise AttributeError(f"Missing required field: {field_name}")

            # Handle nested models.
            value = data[field_name]
            if isinstance(value, dict) and issubclass(field_type, Model):
                value = field_type.from_json(
                    client, cast(dict[str, Any], data[field_name])
                )

            kwargs[field_name] = value

        return cls(client, **kwargs)

    def to_json(self) -> dict[str, Any]:
        """Convert the model instance to a JSON.

        :return: JSON representation of the model instance.
        :rtype: dict[str, Any]
        """
        result: dict[str, Any] = {}
        for field_name, field_value in asdict(self).items():
            value = field_value

            if isinstance(field_value, Model):
                value = field_value.to_json()

            result[field_name] = value

        return result
