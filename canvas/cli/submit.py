"""Canvas LMS Submit Command.
============================

Implements submit command for the CLI.
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from canvasapi import Canvas

from .base import CanvasCommand

__all__ = ("SubmitCommand",)


class SubmitCommand(CanvasCommand):
    """Command to submit an assignment."""

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
        root = self.get_course_root()

        # Read staged files
        staged_file = root / ".canvas" / "staged.json"
        with open(staged_file, "r") as f:
            staged = json.load(f)

        # Print special message if no files are staged
        if not staged:
            print("Files need to be staged before they can be submitted.")
            return

        path, metadata = self.find_first_tracked_parent(Path(staged[0]))

        # If staged files aren't in an assignment folder
        if metadata["type"] != "assignment":
            print("Files aren't associated with any assignment.")
            return

        # Get course
        course_id = self.get_metadata("course_id")
        course = self.client.get_course(course_id)

        # Get assignment
        assignment = course.get_assignment(metadata["id"])

        # Submission files
        print("Uploading submission files...")
        file_ids = []
        for file_path in staged:
            file = assignment.upload_to_submission(file_path)[1]
            file_ids.append(file["id"])

        # Submit assignment
        print("Submitting assignment...")
        assignment.submit(
            {"submission_type": "online_upload", "file_ids": file_ids}
        )

        # Clear staged files
        with open(staged_file, "w") as f:
            json.dump([], f)
