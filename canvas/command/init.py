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
        self.client = client
        self.course_id = args.course_id

    async def _clone_course(self) -> None:
        """Get the course data from the API."""
        # Use data models!!!!!!!!!!!!!!!!!!!!!
        course_info = await self.client.get(
            f"/api/v1/courses/{self.course_id}"
        )
        self.course_name = self._format_name(course_info["name"])

        # there's no way to indicate that the api returns a list

        self.modules = await self.client.get(
            f"/api/v1/courses/{self.course_id}/modules"
        )

        # self.module_names = map(
        #     self._format_name, [mod["name"] for mod in self.modules]
        # )

    def _format_name(self, name):
        return "".join(x for x in name if x.isalnum())

    async def execute(self) -> None:
        """Execute the command."""
        # Get course info from client
        await self._clone_course()

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
        # for module in self.module_names:
        #     os.makedirs(modules_dir / module, exist_ok=True)
