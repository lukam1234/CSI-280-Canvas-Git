"""Canvas LMS Status Command.
============================

Implements status command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace

from canvasapi import Canvas

from canvas.cli.base import CanvasCommand

__all__ = ("StatusCommand",)


class StatusCommand(CanvasCommand):
    """Command to check the status of staged files."""

    def __init__(self, args: Namespace, client: Canvas) -> None:
        """Create command instance from args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: Canvas
        """
        self.client = client

    def execute(self) -> None:
        """Execute the command."""
        root = self.find_course_root()
        staged_file = root / ".canvas" / "staged.json"
        with open(staged_file, "r") as f:
            staged = json.load(f)

        if not staged:
            print("No files are currently staged.")
            exit()

        print("Currently staged:")
        for file in staged:
            print(f"\t{file}")
