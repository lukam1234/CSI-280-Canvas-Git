from __future__ import annotations

from argparse import ArgumentParser

from . import __version__


def gen_parser() -> ArgumentParser:
    """Creates the argument parser for the CLI.
    This is how we'll interact with the Canvas LMS API.

    :return: The `ArgumentParser` with the necessary arguments.
    :rtype: ArgumentParser
    """

    parser = ArgumentParser(prog="canvas")
    parser.add_argument(
        "-v", "--version", action="version", version=f"Printer: {__version__}"
    )

    return parser


def main() -> None:
    """The main entry point for the CLI."""

    parser = gen_parser()
    args = parser.parse_args()

    # Print help if no arguments are passed.
    if not vars(args):
        parser.print_help()


if __name__ == "__main__":
    main()
