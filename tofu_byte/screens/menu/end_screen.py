from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button


from textual import on
from tofu_byte.mystatic import (
    GameDigits,
    Points,
    ThemeScreenTitle,
    YouLoseScreenTitle,
    YouWonScreenTitle,
)

from tofu_byte.screens.const import EDIT_GAME
from tofu_byte.screens.menu.map_loader import MapChain
from tofu_byte.screens.screens import MenuScreenBase


class EndScreen(MenuScreenBase[str]):
    BINDINGS = MenuScreenBase.BINDINGS + [Binding("r", "restart", "Restart game")]

    def __init__(
        self,
        points_collected: int,
        points_max: int,
        game_time_duration: str,
        map_chain: MapChain,
        win: bool,
    ) -> None:
        self.points_collected = points_collected
        self.points_max = points_max
        self.game_time_duration = game_time_duration
        self.map_chain = map_chain
        self.win = win

        super().__init__()

    def compose(self) -> ComposeResult:
        self.points = Points(self.points_collected, self.points_max)
        self.game_time = GameDigits(self.game_time_duration)

        with Container():
            if self.win:
                yield YouWonScreenTitle()
            else:
                yield YouLoseScreenTitle()

        with Container():
            yield self.points
            yield self.game_time

        with Container():
            if self.map_chain.has_next_map() and self.win:
                yield Button("Next level", id="next_level", variant="success")

            yield Button("Restart", id="restart", variant="primary")
            yield Button("Back to Menu", id="to_menu", variant="error")

    def action_restart(self):
        self.dismiss("restart")

    @on(Button.Pressed)
    def to_menu(self, event: Button.Pressed):
        self.dismiss(event.button.id)


class EditEndScreen(MenuScreenBase[str]):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container():
            yield ThemeScreenTitle(EDIT_GAME)

        with Container():
            yield Button("Resume Editing", id="resume", variant="success")
            yield Button("Back to Menu", id="to_menu", variant="error")

    @on(Button.Pressed)
    def to_menu(self, event: Button.Pressed):
        self.dismiss(event.button.id)
