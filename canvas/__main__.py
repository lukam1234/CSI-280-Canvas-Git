from __future__ import annotations

from .command.factory import CommandFactory
from .command.parse import get_parser
from .rest.client import CanvasAPIClient
from .oauth.auth import CanvasAuth
from .utils import CanvasScope


def main() -> None:
    """The main entry point for the CLI."""

    parser = get_parser()
    args = parser.parse_args()

    # Print help if no arguments are passed.
    if not vars(args):
        parser.print_help()
        return

    scopes = (
        CanvasScope.SHOW_ACCESS_TOKEN
        | CanvasScope.CREATE_ACCESS_TOKEN
        | CanvasScope.UPDATE_ACCESS_TOKEN
        | CanvasScope.DELETE_ACCESS_TOKEN
        | CanvasScope.GET_COURSE
        | CanvasScope.GET_MODULE
        | CanvasScope.LIST_COURSES
        | CanvasScope.LIST_MODULES
    )

    authentication = CanvasAuth(
        "PLACEHOLDER", "PLACEHOLDER", "eof-d.codes", scopes=scopes
    )

    client = CanvasAPIClient(authentication)

    # Run the command
    cmd = CommandFactory.from_args(
        args, client  # pyright: ignore reportArgumentType
    )
    cmd.execute()


if __name__ == "__main__":
    main()
