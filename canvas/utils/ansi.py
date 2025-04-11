"""ANSI builder utility.
========================

A simple ANSI builder utility for the command line aspect of our project.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from attrs import define, field

__all__ = ("Mode", "Color", "ANSIBuilder")


class Mode(str, Enum):
    """Holds all supported ANSI modes.

    :ivar ESCAPE: The escape code for ANSI.
    :ivar RESET: The reset code for ANSI.
    :ivar BOLD: The bold code for ANSI.
    :ivar DIM: The dim code for ANSI.
    :ivar UNDERLINE: The underline code for ANSI.
    """

    ESCAPE = "\u001b"
    RESET = "\u001b[0m"
    BOLD = "\u001b[1"
    DIM = "\u001b[2"
    UNDERLINE = "\u001b[4"


class Color(tuple[int, int], Enum):
    """Holds all supported ANSI colors.

    Each enum contains a tuple of two elements, the first being
    the foreground color code, and the second being the background color code.

    :ivar BLACK: The black color code.
    :ivar RED: The red color code.
    :ivar GREEN: The green color code.
    :ivar YELLOW: The yellow color code.
    :ivar BLUE: The blue color code.
    :ivar MAGENTA: The magenta color code.
    :ivar CYAN: The cyan color code.
    :ivar WHITE: The white color code.
    :ivar DEFAULT: The default color code.
    """

    BLACK = 30, 40
    RED = 31, 41
    GREEN = 32, 42
    YELLOW = 33, 43
    BLUE = 34, 44
    MAGENTA = 35, 45
    CYAN = 36, 46
    WHITE = 37, 47
    DEFAULT = 39, 49


@define(slots=True)
class ANSIBuilder:
    """A helper class to build ANSI codeblocks.

    :ivar lines: A list of strings that are the ANSI codeblocks.
    :vartype lines: list[str]
    """

    lines: list[str] = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.lines = []

    def __enter__(self) -> ANSIBuilder:
        return self

    def __exit__(self, *_: Any) -> None:
        self.clear()

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.new(*args, **kwargs)

    def new(
        self,
        text: str,
        *,
        mode: Mode = Mode.BOLD,
        fore: Color = Color.DEFAULT,
        back: Color = Color.DEFAULT,
        reset_after: bool = True,
        new_line: bool = True,
    ) -> None:
        """Creates a new string using the mode passed in.

        :param text: The text to use for the new line.
        :type text: str

        :param mode: The mode to use for the text.
        :type mode: :class:`Mode`

        :param fore: The foreground color to use for the text.
        :type fore: :class:`Color`

        :param back: The background color to use for the text.
        :type back: :class:`Color`

        :param reset_after: Whether to reset the text after the line.
        :type reset_after: bool

        :param new_line: Whether to add a new line after the text.
        :type new_line: bool
        """
        self.lines.append(f"{mode.value};{fore[0]};{back[1]}m{text}")

        if reset_after is not False:
            self.lines.append(Mode.RESET)

        if new_line is True:
            self.lines.append("\n")

    def clear(self) -> None:
        """Clears the current lines of the builder."""
        self.lines.clear()

    @property
    def text(self) -> str:
        """Gets the text of the builder."""
        return "".join(self.lines)
