from __future__ import annotations

from textual.app import RenderResult
from textual.geometry import Offset, Size

from tofu_byte.game.events import EndBallCollected, PointCollected
from tofu_byte.objects.state import BaseState
from tofu_byte.game.collision_manager import CollisionEvent
from tofu_byte.type_register import register
from tofu_byte.objects.game_object import MyText
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

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(1, 1),
        *args: Any,
        **kwargs: Any,
    ):
        if not kwargs.get("anim_state", None):
            star_state = BaseState(
                max_frame=randint(20, 45), animation=["▪", "◆"], frame=randint(0, 20)
            )
            kwargs["anim_state"] = star_state
        super().__init__(
            pos,
            size,
            *args,
            **kwargs,
        )
        self.anim_state.frame = randint(0, self.anim_state.max_frame)

    def default_colors(self) -> tuple[str, str]:
        color = self.app.theme_variables["success"]
        background = self.app.theme_variables["background"]
        return color, background

    def update_logic(self):
        super().update_logic()

    def on_collision(self, event: CollisionEvent) -> None:
        super().on_collision(event)
        if event.obj.type_name == "Player":
            self.post_message(PointCollected(1))
            self.should_remove = True

    def render(self) -> RenderResult:
        style = self.set_colors()
        return MyText(self.anim_state.get_frame(), style=style)


@register
class EndBall(Star):
    type_name = "EndBall"
    blocks: bool = False
    triggers: bool = True
    resizeble: bool = False

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(2, 1),
        *args: Any,
        **kwargs: Any,
    ):
        end_ball_faze = BaseState(
            max_frame=25,
            animation=["🬖🬅", "🬋🬋", "🬈🬢", "🬉🬓", "🬦🬄"],
            frame=randint(0, 10),
        )
        super().__init__(
            pos,
            size,
            *args,
            anim_state=end_ball_faze,
            **kwargs,
        )

    def update_logic(self):
        pass

    def on_collision(self, event: CollisionEvent) -> None:
        super().on_collision(event)
        if event.obj.type_name == "Player":
            self.post_message(EndBallCollected())
            event.obj.win()
            self.should_remove = True
