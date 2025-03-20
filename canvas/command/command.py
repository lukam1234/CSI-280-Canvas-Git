"""Canvas git command.
============================

Implements commands for the CLI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .. import __version__
from ..errors import CLIError
from argparse import ArgumentParser, Namespace
from pathlib import Path

__all__ = (
    "get_parser",
    "CanvasCommand",
    "InitCommand",
    "CommandNotFoundException",
    "NotCanvasCourseException",
)


class CommandNotFoundException(CLIError):
    """Raised when a command isn't recognized."""


class NotCanvasCourseException(CLIError):
    """Raised when a command is run outside a canvas course.

    Note that not all commands need to be run from inside a canvas course.
    """


class CanvasCommand(ABC):
    """Canvas git command which can be executed."""

    @classmethod
    def from_args(cls, args: Namespace):
        """Create command instance from command args.

        :param args: The command args.
        :type args: Namespace
        """
        match args.command:
            case "init":
                return InitCommand(args)
            case _:
                raise CommandNotFoundException

    @classmethod
    def find_course_root(cls) -> Path:
        """Find the root directory of the course."""
        curr_dir = Path.cwd().absolute()

        # Search through parent directories for .canvas folder
        while not (curr_dir / ".canvas").exists():
            curr_dir = curr_dir.parent

            # If root reached, command wasn't run from within course
            if curr_dir == curr_dir.parent:
                raise NotCanvasCourseException

        return curr_dir

    @abstractmethod
    def execute(self):
        """Execute the command."""
        pass


class InitCommand(CanvasCommand):
    """Command to initialize a canvas course."""

    def __init__(self, args):
        """Create init command instance from args.

        :param args: The command args.
        :type args: Namespace
        """
        pass

    def execute(self):
        """Execute the command."""
        pass


def get_parser() -> ArgumentParser:
    """Creates the argument parser for the CLI.
    This is how we'll interact with the Canvas LMS API.

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

    # Subparser for each command
    init_parser = subparser.add_parser("init", help="Initialize the course")
    init_parser.add_argument(
        "-c", "--course_url", help="Url of the canvas course to download"
    )

    return parser
