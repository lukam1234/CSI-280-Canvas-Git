from __future__ import annotations

import os
import asyncio

from canvasapi import Canvas
from dotenv import load_dotenv

from canvas import CanvasScope
from .oauth import CanvasAuth
from canvas.cli.manager import CommandManager

async def main() -> None:
    """The main entry point for the CLI."""

    parser = CommandManager.get_command_parser()
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
        | CanvasScope.UPLOAD_SUBMISSION_FILE
    )

    auth = CanvasAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        canvas_domain="eof-d.codes",
        scopes=scopes,
    )

    await auth.authenticate()
    token = await auth.fetch_token()
    
    client = Canvas(os.getenv("API_URL"), token)

    # Run the command
    cmd = CommandManager.get_command(
        args, client  # pyright: ignore reportArgumentType
    )
    cmd.execute()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
