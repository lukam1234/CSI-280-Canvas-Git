# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import os
from shutil import rmtree
from pathlib import Path
from argparse import Namespace
from unittest.mock import Mock

import pytest
from canvasapi import Canvas
from canvasapi.user import User

from canvas.command.base import NotCanvasCourseException
from canvas.command.init import InitCommand
from canvas.command.factory import CommandFactory, CommandNotFoundException


@pytest.fixture
def mock_client() -> Canvas:
    return Mock(spec=Canvas)


@pytest.fixture
def mock_user() -> User:
    return Mock(spec=User)


@pytest.fixture
def init_command(mock_client: Canvas) -> InitCommand:
    """Init command."""
    return InitCommand(Namespace(command="init", course_id="1"), mock_client)


def test_from_args_init(mock_client: Canvas) -> None:
    """Test creating CanvasCommand from args."""
    init_args = Namespace(command="init", course_id="1")

    assert isinstance(
        CommandFactory.from_args(init_args, mock_client),
        InitCommand,
    )


def test_from_args_fail(mock_client: Canvas) -> None:
    """Test creating CanvasCommand from invalid args."""
    invalid_args = Namespace(command="fake-command")

    with pytest.raises(CommandNotFoundException):
        CommandFactory.from_args(invalid_args, mock_client)


def test_find_course_root_success(init_command: InitCommand) -> None:
    """Test finding the course root from a course."""
    # Create fake course in the testing directory
    file_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    tests_dir = file_dir.parent
    temp_dir = tests_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    canvas_dir = temp_dir / ".canvas"
    canvas_dir.mkdir(exist_ok=True)
    os.chdir(temp_dir)

    # Find course root
    assert init_command.find_course_root() == temp_dir

    # Cleanup fake course
    os.chdir(file_dir)
    rmtree(temp_dir)


def test_find_course_root_fail(init_command: InitCommand) -> None:
    """Test finding the course root when not in a course."""
    with pytest.raises(NotCanvasCourseException):
        init_command.find_course_root()
