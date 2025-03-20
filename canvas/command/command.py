"""Canvas git command.
============================

Implements commands for the CLI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .. import __version__
from argparse import ArgumentParser, Namespace
from pathlib import Path

__all__ = (
    "get_parser",
    "CanvasCommand",
)


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


class CommandNotFoundException(Exception):
    """Exception raised when a command isn't recognized."""

    pass


class NotCanvasCourseException(Exception):
    """Exception raised when a command is run outside a canvas course.

    Note that not all commands need to be run from inside a canvas course.
    """

    pass


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

        def canvas_dir_found():
            return (curr_dir / ".canvas").exists()

        def reached_root():
            return curr_dir == Path.root

        # Search through parent directories for .canvas folder
        while not canvas_dir_found():
            curr_dir = curr_dir.parent

            # If root reached, command not run from within course
            if reached_root():
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
