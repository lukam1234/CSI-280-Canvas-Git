from __future__ import annotations

from command.factory import CommandFactory
from command.parse import get_parser


def main() -> None:
    """The main entry point for the CLI."""

    parser = get_parser()
    args = parser.parse_args()

    # Print help if no arguments are passed.
    if not vars(args):
        parser.print_help()
        return

    # Run the command
    cmd = CommandFactory.from_args(args)  # pyright: ignore reportCallIssue
    cmd.execute()


if __name__ == "__main__":
    main()
