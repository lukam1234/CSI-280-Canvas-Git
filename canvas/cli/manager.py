"""Canvas LMS Command Manager.
============================

Implements a command manager for the CLI.
"""

from __future__ import annotations

from argparse import Namespace, ArgumentParser

from canvasapi import Canvas

from . import CanvasCommand
from .commands import InitCommand
from .commands.add import AddCommand
from .commands.status import StatusCommand
from ..errors import CLIError
from .. import __version__

__all__ = ("CommandManager", "CommandNotFoundException")


class CommandNotFoundException(CLIError):
    """Raised when a command isn't recognized."""


class CommandManager:
    """Manages canvas command building and parsing."""

    COMMANDS = {
        "init": InitCommand,
        "add": AddCommand,
        "status": StatusCommand,
    }

    @classmethod
    def get_command_parser(cls) -> ArgumentParser:
        """Creates the argument parser for the CLI.

        :return: The `ArgumentParser` with the necessary arguments.
        :rtype: ArgumentParser
        """

        parser = ArgumentParser(prog="canvas")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"Canvas Git: {__version__}",
        )

        subparser = parser.add_subparsers(dest="command", help="Commands")

        # Init Command
        init_parser = subparser.add_parser(
            "init", help="Initialize the course"
        )
        init_parser.add_argument(
            "-c", "--course_id", help="ID of the canvas course to download"
        )

        # Add command
        add_cmd_parser = subparser.add_parser(
            "add", help="Add a file to be staged"
        )
        add_cmd_parser.add_argument(
            "-f", "--file_path", help="Path of the file to be staged"
        )

        # Status command
        subparser.add_parser("status", help="Check the status of staged files")

        return parser

    @classmethod
    def get_command(cls, args: Namespace, client: Canvas) -> CanvasCommand:
        """Create command instance from command args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: Canvas

        :return: Command created from the given args that can be executed.
        :rtype: CanvasCommand
        """
        if args.command not in cls.COMMANDS:
            raise CommandNotFoundException

        return cls.COMMANDS[args.command](args, client)
