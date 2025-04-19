"""Canvas LMS Stage Command.
============================

Implements stage command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from canvasapi import Canvas

from canvas.cli.base import CanvasCommand, NotCanvasCourseException

__all__ = ("StageCommand",)


class StageCommand(CanvasCommand):
    """Command to stage a file for submission."""

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

        # Exit if the file doesn't exist
        if not file_to_stage.exists():
            print(
                str(CanvasCommand.get_rel_path(file_to_stage)),
                "does not exist.",
            )
            return

        print(f"Staging {str(CanvasCommand.get_rel_path(file_to_stage))}")

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

        # Exit if already staged
        if str(file_to_stage) in staged:
            print(
                str(CanvasCommand.get_rel_path(file_to_stage)),
                "is already staged.",
            )
            return

        # Exit if outside an assignment folder
        if (
            self.find_first_tracked_parent(file_to_stage)[1]["type"]
            != "assignment"
        ):
            print("Staging assignment is ambiguous in this context.")
            print("Move your file into an assignment's folder.")
            return

        # Exit if assignment folders vary between staged files
        if staged and (
            self.find_first_tracked_parent(file_to_stage)[0]
            != self.find_first_tracked_parent(Path(staged[0]))[0]
        ):
            print(
                "Cannot stage files for multiple assignments at the same time."
                "The specified file\nis in the folder of a separate assignment"
                " than previously staged files. Move\nthe file to the same"
                "assignment folder as previously staged files or unstage the\n"
                "currently staged files and try staging again."
            )
            return

        # Write staged file paths with new one appended
        staged.append(str(file_to_stage))
        with open(staged_file, "w") as f:
            json.dump(staged, f)

        print(
            "Staging complete for",
            str(CanvasCommand.get_rel_path(file_to_stage)),
        )
