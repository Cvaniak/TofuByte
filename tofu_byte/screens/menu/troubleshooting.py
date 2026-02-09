from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    VerticalScroll,
)
from textual.widgets import Button, Markdown, Static
from tofu_byte.config import RESOURCES_DIR
from tofu_byte.screens.const import TROUBLESHOOTING
from tofu_byte.mystatic import PrimaryScreenTitle


from tofu_byte.screens.screens import MenuScreenBase


class ListStatic(Horizontal):
    def __init__(self, left: str, right: str) -> None:
        self.left = left
        self.right = right
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(self.left, classes="left")
        yield Static(self.right, classes="right")


class Troubleshooting(MenuScreenBase):
    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(TROUBLESHOOTING)
            readme_path = RESOURCES_DIR / "TROUBLESHOOTING.md"
            markdown = Markdown(readme_path.read_text(encoding="utf-8"))
            yield markdown
        # yield Markdown(readme_path.read_text(encoding="utf-8"))

        with VerticalScroll():
            yield ListStatic(
                "▂▂" * 5 + "\n" + "◢◣" * 5 + "\n" + "▆▆" * 5,
                "The most sense it has if there is no gap at the bottom",
            )
            yield ListStatic("█" * 10, "There should be no gaps between blocks")
            yield ListStatic(
                "█ " * 5 + "\n" + "▐▌" * 5 + "\n" + " █" * 5 + "\n" + "▌▐" * 5,
                "Should be repeatable pattern",
            )
            yield ListStatic(
                "▂" * 10 + "\n" + "█" * 10,
                "There should be no gap between top and bottom",
            )
            yield ListStatic("◆ ▪", "Not that important, just rhombus and square")
        with Container():
            yield Button("Back", id="back", variant="error")
