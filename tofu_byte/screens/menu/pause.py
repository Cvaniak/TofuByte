from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button
from tofu_byte.screens.const import PAUSE_MENU


from textual import on
from tofu_byte.mystatic import PrimaryScreenTitle


from tofu_byte.screens.screens import MenuScreenBase


class PauseMenu(MenuScreenBase[str]):
    BINDINGS = [
        Binding("tab,j,s,down", "app.focus_next", "Focus Next", show=False),
        Binding("shift+tab,k,w,up", "app.focus_previous", "Focus Previous", show=False),
        Binding("escape", "app.pop_screen", "Resume"),
        Binding("r", "restart", "Restart game"),
    ]

    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(PAUSE_MENU)

        with Container():
            yield Button("Restart", id="restart", variant="warning")
            yield Button("Resume", id="resume", variant="primary")
            yield Button("Discard Game", id="discard", variant="error")

    def action_restart(self):
        self.dismiss("restart")

    @on(Button.Pressed, "#resume")
    def resume(self, event: Button.Pressed):
        self.dismiss("resume")

    @on(Button.Pressed, "#discard")
    async def discard(self, event: Button.Pressed):
        self.dismiss("discard")

    @on(Button.Pressed, "#restart")
    async def restart(self, event: Button.Pressed):
        self.dismiss("restart")
