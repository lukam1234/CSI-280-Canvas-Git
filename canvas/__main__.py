from __future__ import annotations

from command.command import get_parser, CanvasCommand


def main() -> None:
    """The main entry point for the CLI."""

    parser = get_parser()
    args = parser.parse_args()

    # Print help if no arguments are passed.
    if not vars(args):
        parser.print_help()
        return

    # Run the command
    cmd = CanvasCommand.from_args(args)
    cmd.execute()


if __name__ == "__main__":
    main()
