from typing import Any
from rich.style import Style
from rich.text import Text
from textual.app import RenderResult
from textual.geometry import Offset, Size

from tofu_byte.objects.faze import Faze
from tofu_byte.type_register import register
from .base_object import BaseObject
from random import randint

light_faze = Faze(0, 8, ["🬷", "🬳", "🬯", "🬶", "🬲", "🬮", "▟"])


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
        super().__init__(pos, size, *args, **kwargs)
        self.animation = light_faze
        self.animation.frame = randint(0, self.animation.max_frame)

    def default_colors(self) -> tuple[str, str]:
        color = self.app.theme_variables["warning"]
        background = self.app.theme_variables["background"]
        return color, background

    def reload(self) -> None:
        if randint(0, 2):
            return

        new_frame = self.render()
        if new_frame != self.curr_frame:
            self.curr_frame = new_frame
            self.update(new_frame)

    def render(self) -> RenderResult:
        vars = self.app.theme_variables
        text = Text()
        text.append(
            self.animation.get_random_frame(),
            style=Style(color=vars["error"], bgcolor=vars["background"]),
        )
        text.append(
            "🬗", style=Style(color=vars["warning"], bgcolor=vars["warning-darken-3"])
        )
        return text
