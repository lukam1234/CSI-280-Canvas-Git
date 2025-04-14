from __future__ import annotations

import os
from canvasapi import Canvas
from dotenv import load_dotenv

from canvas.cli.manager import CommandManager


def main() -> None:
    """The main entry point for the CLI."""

    parser = CommandManager.get_command_parser()
    args = parser.parse_args()

    # Print help if no arguments are passed.
    if not vars(args):
        parser.print_help()
        return

    API_URL = os.getenv("API_URL")
    API_KEY = os.getenv("API_KEY")
    client = Canvas(API_URL, API_KEY)

    # Run the command
    cmd = CommandManager.get_command(
        args, client  # pyright: ignore reportArgumentType
    )
    cmd.execute()


if __name__ == "__main__":
    load_dotenv()
    main()
