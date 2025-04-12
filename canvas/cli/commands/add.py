"""Canvas LMS Add Command.
============================

Implements add command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from canvasapi import Canvas

from canvas.cli.base import CanvasCommand

__all__ = ("AddCommand",)


class AddCommand(CanvasCommand):
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
        file_to_stage = Path(self.file_path)
        if not file_to_stage.exists():
            print(str(file_to_stage), "does not exist.")
            exit()

        print(f"Staging {str(file_to_stage)}")

        root = self.find_course_root()
        staged_file = root / ".canvas" / "staged.json"

        # Get currently staged and append the new path
        with open(staged_file, "r") as f:
            staged = json.load(f)
        staged.append(str(file_to_stage.absolute()))
        with open(staged_file, "w") as f:
            json.dump(staged, f)

        print(f"Staging complete for {str(file_to_stage)}")
