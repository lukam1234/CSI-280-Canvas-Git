"""Canvas LMS Init Command.
============================

Implements init command for the CLI.
"""

from __future__ import annotations

from argparse import Namespace

from ..rest import CanvasAPIClient
from .base import CanvasCommand

__all__ = ("InitCommand",)


class InitCommand(CanvasCommand):
    """Command to initialize a canvas course."""

    def __init__(self, args: Namespace, client: CanvasAPIClient) -> None:
        """Create init command instance from args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: CanvasAPIClient
        """
        pass

    def execute(self) -> None:
        """Execute the command."""
        pass
