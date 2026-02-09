from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Link, Static
from tofu_byte.screens.const import ABOUT, ABOUT_AUTHOR_BODY
from tofu_byte.mystatic import PrimaryScreenTitle


from tofu_byte.screens.screens import MenuScreenBase


class About(MenuScreenBase):
    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(ABOUT)
        with Container(classes="body"):
            with Container(classes="wrapper"):
                yield Link(
                    "⭐ Give a star on Github ⭐",
                    url="https://github.com/Cvaniak/TofuByte",
                    tooltip="Cvaniak/TofuByte",
                )
                yield Static(ABOUT_AUTHOR_BODY)
        with Container():
            yield Button("Back", id="back", variant="error")
