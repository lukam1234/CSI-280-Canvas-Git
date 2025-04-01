"""Canvas LMS Init Command.
============================

Implements init command for the CLI.
"""

from __future__ import annotations

from argparse import Namespace
import os
from pathlib import Path

from ..rest import CanvasAPIClient
from .base import CanvasCommand

__all__ = ("InitCommand",)


class InitCommand(CanvasCommand):
    """Command to initialize a canvas course."""

    def __init__(self, args: Namespace, client: CanvasAPIClient) -> None:
        """Create init command instance from args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: CanvasAPIClient
        """
        self.course_url = args.course_url
        self.course_name = "COURSE_NAME"

    def execute(self) -> None:
        """Execute the command."""
        curr_dir = Path.cwd().absolute()
        course_dir = curr_dir / self.course_name
        canvas_dir = course_dir / ".canvas"

        # Create .canvas folder
        os.makedirs(canvas_dir, exist_ok=True)

        # Create files in .canvas folder
        open(f"{canvas_dir}/config.json", "a").close()
        open(f"{canvas_dir}/token.json", "a").close()
        open(f"{canvas_dir}/staged.json", "a").close()
        open(f"{canvas_dir}/metadata.json", "a").close()

        # Create modules folder
        modules_dir = course_dir / "modules"
        os.makedirs(modules_dir, exist_ok=True)
        os.makedirs(modules_dir / "module-1", exist_ok=True)
        os.makedirs(modules_dir / "module-2", exist_ok=True)
