from . import __version__
from argparse import ArgumentParser

def gen_parser() -> ArgumentParser:
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
        version=f"Printer: {__version__}"
    )

    return parser

def main() -> None:
    parser = gen_parser()
    args = parser.parse_args()

    if not vars(args):
        parser.print_help()

if __name__ == "__main__":
    main()