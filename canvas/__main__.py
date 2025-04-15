from __future__ import annotations

import os

from canvasapi import Canvas
from dotenv import load_dotenv

from .command.factory import CommandFactory
from .command.parse import get_parser


def main() -> None:
    """The main entry point for the CLI."""

    parser = get_parser()
    args = parser.parse_args()

    # Print help if no arguments are passed.
    if not vars(args):
        parser.print_help()
        return

    API_URL = os.getenv("API_URL")
    API_KEY = os.getenv("API_KEY")

    client = Canvas(API_URL, API_KEY)

    # Run the command
    cmd = CommandFactory.from_args(
        args, client  # pyright: ignore reportArgumentType
    )
    cmd.execute()


if __name__ == "__main__":
    load_dotenv()
    main()
