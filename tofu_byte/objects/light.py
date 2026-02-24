from typing import Any
from rich.style import Style
from rich.text import Text
from textual.app import RenderResult
from textual.geometry import Offset, Size

from tofu_byte.objects.state import RandomFrameState
from tofu_byte.type_register import register
from .base_object import BaseObject
from random import randint, shuffle


@register
class Light(BaseObject):
    type_name = "Light"
    blocks: bool = False
    triggers: bool = False
    resizeble: bool = False

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(1, 2),
        r: int = 1,
        visible: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        frames = ["🬷", "🬳", "🬯", "🬶", "🬲", "🬮", "▟"]
        shuffle(frames)
        light_faze = RandomFrameState(
            max_frame=randint(32, 64),
            animation=frames,
            frame=0,
        )
        super().__init__(pos, size, anim_state=light_faze, *args, **kwargs)
        self.anim_state.frame = randint(0, self.anim_state.max_frame)

    def default_colors(self) -> tuple[str, str]:
        color = self.app.theme_variables["warning"]
        background = self.app.theme_variables["background"]
        return color, background

    def update_logic(self) -> None:
        super().update_logic()

    def render(self) -> RenderResult:
        vars = self.app.theme_variables
        text = Text()
        text.append(
            self.anim_state.get_frame(),
            style=Style(color=vars["error"], bgcolor=vars["background"]),
        )
        text.append(
            "🬗", style=Style(color=vars["warning"], bgcolor=vars["warning-darken-3"])
        )
        return text
