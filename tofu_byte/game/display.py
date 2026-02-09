from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.geometry import Size
from textual.widget import Widget
from rich.color import Color
from tofu_byte.game.events import DisplayClicked, DisplayMouseHover
from tofu_byte.mystatic import GameObjectStatic


class Display(Container):
    def __init__(
        self,
        screen_size: Size = Size(66, 34),
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        color: str = "#444444",
        border_color: str = "#ffaa00",
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.drawables: list[GameObjectStatic] = []
        self.can_focus = True
        self.screen_size = screen_size
        self.styles.min_width = self.styles.max_width = screen_size.width
        self.styles.min_height = self.styles.min_height = screen_size.height

        self.color = Color.parse(color)
        self.border_color = Color.parse(border_color)

        self.watch(self.app, "theme", self.on_theme_change, init=False)

    def resort_layers(self):
        layers = tuple(["bg", *sorted(x.layer for x in self.drawables), "fg"])
        self.screen.styles.layers = layers

    def compose(self) -> ComposeResult:
        yield from self.drawables

    def mount_drawable(self, drawable: GameObjectStatic) -> None:
        self.drawables.append(drawable)
        self.mount(drawable)
        self.is_draggin = False
        self.can_focus = False
        self.resort_layers()

    def delete_drawable(self, drawable: GameObjectStatic) -> None:
        self.drawables = [note for note in self.drawables if note != drawable]
        self.remove_children([drawable])
        drawable.remove()
        self.resort_layers()

    def clear_all(self):
        to_remove = list(self.drawables)
        self.remove_children(to_remove)
        for drawable in list(to_remove):
            drawable.remove()
        self.drawables = []

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        self.post_message(DisplayClicked(event))

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.post_message(DisplayMouseHover(event))

    def on_theme_change(self, new_value: str) -> None:
        self.styles.background = self.app.available_themes[new_value].background
