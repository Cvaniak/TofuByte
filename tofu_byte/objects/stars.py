from __future__ import annotations

from textual.app import RenderResult
from textual.geometry import Offset, Size

from tofu_byte.game.events import EndBallCollected, PointCollected
from tofu_byte.objects.faze import Faze
from tofu_byte.player.collision import CollisionEvent
from tofu_byte.type_register import register
from tofu_byte.mystatic import MyText
from .base_object import BaseObject
from random import randint
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@register
class Star(BaseObject):
    type_name = "Star"
    blocks: bool = False
    triggers: bool = True
    resizeble: bool = False
    frames: list[str] = ["▪", "◆"]

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(1, 1),
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(pos, size, *args, **kwargs)
        self.animation = Faze(
            0,
            randint(10, 20),
            self.frames,
        )
        self.update(self.render())

    def default_colors(self) -> tuple[str, str]:
        color = self.app.theme_variables["success"]
        background = self.app.theme_variables["background"]
        return color, background

    def reload(self):
        if randint(0, 2):
            return

        new_frame = self.render()
        if new_frame != self.curr_frame:
            self.curr_frame = new_frame
            self.update(new_frame)

    def on_collision(self, event: CollisionEvent) -> None:
        self.post_message(PointCollected(1))
        self.should_remove = True

    def render(self) -> RenderResult:
        style = self.set_colors()
        return MyText(self.animation.get_frame(), style=style)


@register
class EndBall(Star):
    type_name = "EndBall"
    blocks: bool = False
    triggers: bool = True
    resizeble: bool = False
    frames: list[str] = [
        "🬖🬅",
        "🬋🬋",
        "🬈🬢",
        "🬉🬓",
        "🬦🬄",
    ]

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(2, 1),
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(pos, size, *args, **kwargs)
        self.animation = Faze(
            0,
            25,
            self.frames,
        )
        self.update(self.render())

    def reload(self):
        new_frame = self.render()
        if new_frame != self.curr_frame:
            self.curr_frame = new_frame
            self.update(new_frame)

    def on_collision(self, event: CollisionEvent) -> None:
        self.post_message(EndBallCollected())
        event.player.win()
        self.should_remove = True
