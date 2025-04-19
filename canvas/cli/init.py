"""Canvas LMS Init Command.
============================

Implements init command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from canvasapi import Canvas
from canvasapi.module import Module

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

    def _format_filename(self, name):
        return "".join(x for x in name if x.isalnum())

    def _create_hidden_folder(
        self, root_dir: Path, metadata: dict[str, Any]
    ) -> None:
        """Creates the .canvas folder."""
        # Create .canvas folder
        canvas_dir = root_dir / ".canvas"
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

    def _clone_module_item(self, item, module_dir: Path) -> dict[str, Any]:
        """Get the item data from the API."""
        if item.type == "Assignment":
            # Create assignment folder
            assignment_dir = module_dir / self._format_filename(item.title)
            assignment_dir.mkdir(parents=True, exist_ok=True)

            # Create .info folder
            info_dir = assignment_dir / ".info"
            info_dir.mkdir(parents=True, exist_ok=True)

            # Download description
            assignment = self.course.get_assignment(item.content_id)
            description_file = info_dir / "description.md"
            description_file.write_text(assignment.description)

            # Add assignment metadata
            return {
                str(assignment_dir): {
                    "type": "assignment",
                    "id": item.content_id,
                }
            }
        elif item.type == "File":
            # Download file
            file = self.course.get_file(item.content_id)
            file_dir = str(module_dir / file.display_name)
            file.download(file_dir)

            # Add file metadata
            return {
                str(file_dir): {
                    "type": "file",
                    "id": item.content_id,
                }
            }

        return {}

    def _clone_module(
        self, module: Module, module_dir: Path
    ) -> dict[str, Any]:
        """Get the module and data from the API."""
        module_dir.mkdir(parents=True, exist_ok=True)

        # Track module metadata
        module_metadata = {
            str(module_dir): {
                "type": "module",
                "id": module.id,
            }
        }

        # Download assignments & files
        for item in module.get_module_items():
            module_metadata.update(self._clone_module_item(item, module_dir))

        return module_metadata

    def _clone_course(self) -> None:
        """Get the course data from the API."""
        # No course id was supplied
        if self.course_id is None:
            # Change to showing them a list and asking them to choose
            print("--course_id flag is required")
            return

        print("Initializing course...")
        self.course = self.client.get_course(self.course_id)

        # Determine course folder
        curr_dir = CanvasCommand.get_current_dir()
        course_dir = curr_dir / self._format_filename(self.course.name)

        # If the course was already cloned, exit
        if course_dir.exists():
            print(
                "Course has already been initialized in this directory."
                "\nDelete the course files or initialize somewhere else."
            )
            return

        # Create course folder
        course_dir.mkdir(parents=True, exist_ok=True)

        # Create modules folder
        modules_dir = course_dir / "Modules"
        modules_dir.mkdir(parents=True, exist_ok=True)

        # Create module folders
        print("Downloading modules...")
        course_metadata = {"course_id": self.course_id}
        for module in self.course.get_modules():
            module_dir = modules_dir / self._format_filename(module.name)
            course_metadata.update(self._clone_module(module, module_dir))

        print("Creating hidden folder...")
        self._create_hidden_folder(course_dir, course_metadata)

        print(f"Course initialized at {course_dir}")

    def execute(self) -> None:
        """Execute the command."""
        self._clone_course()
