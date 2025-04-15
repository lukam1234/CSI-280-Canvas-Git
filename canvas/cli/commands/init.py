"""Canvas LMS Init Command.
============================

Implements init command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from canvasapi import Canvas

from canvas.cli.base import CanvasCommand

__all__ = ("InitCommand",)


class InitCommand(CanvasCommand):
    """Command to initialize a canvas course."""

    def __init__(self, args: Namespace, client: Canvas) -> None:
        """Create init command instance from args.

        :param args: Command args.
        :type args: Namespace

        :param client: API client for when API calls are needed.
        :type client: Canvas
        """
        self.client = client
        self.course_id = args.course_id

    def _clone_course(self) -> None:
        """Get the course data from the API."""
        self.course = self.client.get_course(self.course_id)
        # if course_id not supplied, show them list and ask them to choose

    def _format_name(self, name):
        return "".join(x for x in name if x.isalnum())

    def execute(self) -> None:
        """Execute the command."""
        if self.course_id is None:
            print("--course_id flag is required")
            exit()

        print("Initializing course...")

        self._clone_course()
        metadata = {"course_id": self.course_id}

        curr_dir = Path.cwd().absolute()
        course_dir = curr_dir / self._format_name(self.course.name)

        if course_dir.exists():
            print(
                "Course has already been initialized in this directory."
                "\nDelete the course files or initialize somewhere else."
            )
            exit()

        # Create modules folder
        print("Downloading modules...")
        modules_dir = course_dir / "Modules"
        modules_dir.mkdir(parents=True, exist_ok=True)
        for module in self.course.get_modules():
            # Create module folder
            module_dir = modules_dir / self._format_name(module.name)
            module_dir.mkdir(parents=True, exist_ok=True)

            # Add module metadata
            metadata[str(module_dir)] = {
                "type": "module",
                "id": module.id,
            }

            # Download assignments & files
            for item in module.get_module_items():
                if item.type == "Assignment":

                    # Create assignment and .info folder
                    assignment_dir = module_dir / self._format_name(item.title)
                    info_dir = assignment_dir / ".info"
                    assignment_dir.mkdir(parents=True, exist_ok=True)
                    info_dir.mkdir(parents=True, exist_ok=True)

                    # Download description
                    assignment = self.course.get_assignment(item.content_id)
                    description_file = info_dir / "description.md"
                    description_file.write_text(assignment.description)

                    # Add assignment metadata
                    metadata[str(assignment_dir)] = {
                        "type": "assignment",
                        "id": item.content_id,
                    }

                if item.type == "File":
                    # Download file
                    file = self.course.get_file(item.content_id)
                    file.download(str(module_dir / file.display_name))

        # Create .canvas folder
        canvas_dir = course_dir / ".canvas"
        canvas_dir.mkdir(parents=True, exist_ok=True)

        # Create files in .canvas folder
        metadata_file = canvas_dir / "metadata.json"
        staged_file = canvas_dir / "staged.json"
        config_file = canvas_dir / "config.json"
        token_file = canvas_dir / "token.json"

        with open(metadata_file, "w") as f:
            json.dump(metadata, f)
        with open(staged_file, "w") as f:
            json.dump([], f)
        with open(config_file, "w") as f:
            json.dump({}, f)
        with open(token_file, "w") as f:
            json.dump({}, f)

        print(f"Course initialized at {course_dir}")
