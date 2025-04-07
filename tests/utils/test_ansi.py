from __future__ import annotations

import pytest

from canvas import ANSIBuilder, Mode, Color


def test_context_manager() -> None:
    """Test the context manager for ANSIBuilder."""
    with ANSIBuilder() as builder:
        builder("foo")
        builder("bar")

    assert len(builder.lines) == 0
    assert builder.lines == []
    assert builder.text == ""


def test_call() -> None:
    """Test the `__call__` method of ANSIBuilder."""
    with ANSIBuilder() as builder:
        builder("foo", mode=Mode.BOLD, fore=Color.RED, back=Color.GREEN)

        assert len(builder.lines) == 3
        assert builder.lines == [
            f"{Mode.BOLD.value};{Color.RED[0]};{Color.GREEN[1]}mfoo",
            Mode.RESET.value,
            "\n",
        ]


@pytest.mark.parametrize(
    "text,mode,fore,back,reset_after,new_line,expected_parts",
    [
        (
            "foo",
            Mode.BOLD,
            Color.DEFAULT,
            Color.DEFAULT,
            True,
            True,
            [
                f"{Mode.BOLD.value};{Color.DEFAULT[0]};{Color.DEFAULT[1]}mfoo",
                Mode.RESET,
                "\n",
            ],
        ),
        (
            "bar",
            Mode.BOLD,
            Color.RED,
            Color.DEFAULT,
            True,
            True,
            [
                f"{Mode.BOLD.value};{Color.RED[0]};{Color.DEFAULT[1]}mbar",
                Mode.RESET,
                "\n",
            ],
        ),
        (
            "baz",
            Mode.BOLD,
            Color.DEFAULT,
            Color.DEFAULT,
            False,
            True,
            [
                f"{Mode.BOLD.value};{Color.DEFAULT[0]};{Color.DEFAULT[1]}mbaz",
                "\n",
            ],
        ),
        (
            "qux",
            Mode.BOLD,
            Color.DEFAULT,
            Color.DEFAULT,
            True,
            False,
            [
                f"{Mode.BOLD.value};{Color.DEFAULT[0]};{Color.DEFAULT[1]}mqux",
                Mode.RESET,
            ],
        ),
    ],
)
def test_new(
    text: str,
    mode: Mode,
    fore: Color,
    back: Color,
    reset_after: bool,
    new_line: bool,
    expected_parts: list[str],
) -> None:
    """Test creating new ANSI text."""
    with ANSIBuilder() as builder:
        builder.new(
            text,
            mode=mode,
            fore=fore,
            back=back,
            reset_after=reset_after,
            new_line=new_line,
        )

        assert len(builder.lines) == len(expected_parts)
        assert builder.lines == expected_parts


def test_clear() -> None:
    """Test the clear method of ANSIBuilder."""
    with ANSIBuilder() as builder:
        builder("foo")
        builder("bar")
        builder.clear()

        assert len(builder.lines) == 0
        assert builder.lines == []


def test_text() -> None:
    """Test the text property that joins all lines."""
    with ANSIBuilder() as builder:
        builder("foo", mode=Mode.BOLD, fore=Color.RED)
        builder("bar", mode=Mode.UNDERLINE, fore=Color.BLUE)

        expected = "".join(
            [
                f"{Mode.BOLD.value};{Color.RED[0]};{Color.DEFAULT[1]}mfoo",
                Mode.RESET,
                "\n",
                f"{Mode.UNDERLINE.value};{Color.BLUE[0]};{Color.DEFAULT[1]}mbar",
                Mode.RESET,
                "\n",
            ]
        )

        assert builder.text == expected
