"""Canvas LMS Command Factory.
============================

Implements command factory for the CLI.
"""

from __future__ import annotations

from argparse import Namespace

from canvasapi import Canvas

from ..errors import CLIError
from .base import CanvasCommand
from .init import InitCommand

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
            case _:
                raise CommandNotFoundException
