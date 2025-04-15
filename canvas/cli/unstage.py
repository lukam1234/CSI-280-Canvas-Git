"""Canvas LMS Unstage Command.
============================

Implements unstage command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from canvasapi import Canvas

from canvas.cli.base import CanvasCommand, NotCanvasCourseException

__all__ = ("UnstageCommand",)


class UnstageCommand(CanvasCommand):
    """Command to unstage a file for submission."""

    def __init__(self, args: Namespace, client: Canvas) -> None:
        """Create command instance from args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: Canvas
        """
        self.client = client
        self.file_path = args.file_path

    def execute(self) -> None:
        """Execute the command."""
        file_to_stage = Path(self.file_path).resolve()

        print(f"Unstaging {str(CanvasCommand.get_rel_path(file_to_stage))}")

        # Ensure command is run from within course
        try:
            root = self.get_course_root()
        except NotCanvasCourseException:
            print("Must be run from inside a canvas course.")
            return

        # Read currently staged paths
        staged_file = root / ".canvas" / "staged.json"
        with open(staged_file, "r") as f:
            staged = json.load(f)

        # Exit if not already staged
        if str(file_to_stage) not in staged:
            print(
                str(CanvasCommand.get_rel_path(file_to_stage)),
                "is not staged.",
            )
            return

        # Write staged file paths with the specified file unstaged
        staged.remove(str(file_to_stage))
        with open(staged_file, "w") as f:
            json.dump(staged, f)

        print(
            "Unstaging complete for "
            + str(CanvasCommand.get_rel_path(file_to_stage))
        )
