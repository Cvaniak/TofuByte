from __future__ import annotations

from textual.app import App
from textual.binding import Binding
from tofu_byte.config import get_setting, set_setting
from tofu_byte.screens.menu.about import About
from tofu_byte.screens.menu.map_loader import MapEditor, MapLoader
from tofu_byte.screens.menu.menu import Menu

from tofu_byte.screens.menu.pause import PauseMenu
from tofu_byte.screens.menu.troubleshooting import Troubleshooting
from tofu_byte.themes import TOFU_BUILTIN_THEMES


class GameMenu(App[None]):
    CSS_PATH = [
        "css/main.css",
        "css/game_scene.css",
        "css/menu_screens.css",
        "css/debug.css",
    ]

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("[", "previous_theme", "Previous theme"),
        Binding("]", "next_theme", "Next theme"),
    ]
    SCREENS = {
        "menu": Menu,
        "map_loader": MapLoader,
        "map_editor": MapEditor,
        "pause_menu": PauseMenu,
        "troubleshooting": Troubleshooting,
        "about": About,
    }

    def __init__(
        self,
    ):
        super().__init__()
        for name, theme in TOFU_BUILTIN_THEMES.items():
            self.register_theme(theme)
        self.theme_names = [name for name, _ in TOFU_BUILTIN_THEMES.items()]
        if theme := get_setting("theme", self.theme_names[0]):
            self.theme = theme

    def on_mount(self):
        self.push_screen("menu")

    def action_next_theme(self) -> None:
        themes = self.theme_names
        try:
            index = themes.index(self.current_theme.name)
        except ValueError:
            index = 0
        self.theme = themes[(index + 1) % len(themes)]
        self.notify_new_theme(self.current_theme.name)
        set_setting("theme", self.theme)

    def action_previous_theme(self) -> None:
        themes = self.theme_names
        index = themes.index(self.current_theme.name)
        self.theme = themes[(index - 1) % len(themes)]
        self.notify_new_theme(self.current_theme.name)
        set_setting("theme", self.theme)

    def notify_new_theme(self, theme_name: str) -> None:
        self.clear_notifications()
        self.notify(f"Theme is {theme_name}")


if __name__ == "__main__":
    app = GameMenu()
    app.run()  # type: ignore
