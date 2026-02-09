from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Footer
from tofu_byte.config import GAME_VERSION
from tofu_byte.screens.const import MENU_TEXT


from textual import on
from tofu_byte.mystatic import PrimaryScreenTitle

from tofu_byte.screens.game_display import GameScreenContainer, EditorScreenContainer
from tofu_byte.screens.menu.map_loader import MapChain
from tofu_byte.screens.screens import MenuScreenBase


class Menu(MenuScreenBase[None]):
    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(MENU_TEXT)
        with Container():
            yield Button("Start Game", id="map_loader", variant="success")
            yield Button("Edit Map", id="map_editor", variant="primary")
            yield Button("Troubleshooting", id="troubleshooting", variant="primary")
            yield Button("About", id="about", variant="primary")
            yield Button("Quit", id="quit", variant="error")
            yield PrimaryScreenTitle(f"version: {GAME_VERSION}", classes="version")
        yield Footer()

    def on_back_from_game(self, map_chain: MapChain):
        if map_chain:
            self.app.push_screen(GameScreenContainer(map_chain), self.on_back_from_game)

    def on_load_game(self, map_chain: MapChain) -> None:
        self.app.push_screen(GameScreenContainer(map_chain), self.on_back_from_game)

    def on_load_map_editor(self, map_chain: MapChain) -> None:
        self.app.push_screen(EditorScreenContainer(map_chain))

    @on(Button.Pressed, "#map_loader")
    async def map_loader(self):
        self.app.push_screen("map_loader", self.on_load_game)

    @on(Button.Pressed, "#map_editor")
    async def map_editor(self):
        self.app.push_screen("map_editor", self.on_load_map_editor)

    @on(Button.Pressed, "#troubleshooting")
    def troubleshooting(self):
        self.app.push_screen("troubleshooting")

    @on(Button.Pressed, "#quit")
    def quit_game(self):
        self.app.exit()

    @on(Button.Pressed, "#about")
    def about_author(self):
        self.app.push_screen("about")

    def action_go_back(self): ...
