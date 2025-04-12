"""Canvas LMS Command Factory.
============================

Implements command factory for the CLI.
"""

from __future__ import annotations

from argparse import Namespace

from canvasapi import Canvas

from .commands.init import InitCommand
from .commands.add import AddCommand
from .commands.status import StatusCommand
from ..errors import CLIError
from .base import CanvasCommand

__all__ = ("CommandFactory", "CommandNotFoundException")


class CommandNotFoundException(CLIError):
    """Raised when a command isn't recognized."""


class CommandFactory:
    """Canvas git command builder."""

    @classmethod
    def from_args(cls, args: Namespace, client: Canvas) -> CanvasCommand:
        """Create command instance from command args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: Canvas

        :return: Command created from the given args that can be executed.
        :rtype: CanvasCommand
        """
        match args.command:
            case "init":
                return InitCommand(args, client)
            case "add":
                return AddCommand(args, client)
            case "status":
                return StatusCommand(args, client)
            case _:
                raise CommandNotFoundException
