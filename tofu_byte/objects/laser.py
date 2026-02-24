from __future__ import annotations
from random import choice, randint
from typing import Any
from textual.geometry import Offset, Size
from textual.app import RenderResult
from rich.style import Style
from rich.color import Color, blend_rgb
import colorsys

from tofu_byte.objects.game_object import MyText
from tofu_byte.game.collision_manager import CollisionEvent
from .base_object import BaseObject


class Laser(BaseObject):
    type_name = "Laser"
    blocks: bool = False
    triggers: bool = True
    adjust = True

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(8, 1),
        lifetime: int = 10,
        direction: Offset = Offset(1, 0),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pos, size, *args, **kwargs)
        self.lifetime = lifetime
        self.direction = direction
        self.age = 0

    def update_logic(self) -> None:
        self.age += 1
        if self.age >= self.lifetime:
            self.should_remove = True

    def on_collision(self, event: CollisionEvent) -> None:
        if event.obj.type_name == "Player":
            if self.get_occupied_cells() & event.obj.get_occupied_cells():
                event.obj.damage()

    @staticmethod
    def _adjust_luminance_rich_color(rich_color: Color, factor: float) -> Color:
        if rich_color.triplet is None:
            rgb_tuple = rich_color.get_truecolor()
        else:
            rgb_tuple = rich_color.triplet

        r_255, g_255, b_255 = rgb_tuple

        r_norm, g_norm, b_norm = r_255 / 255.0, g_255 / 255.0, b_255 / 255.0

        h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

        l = max(0.0, min(1.0, l + factor))

        r_new_norm, g_new_norm, b_new_norm = colorsys.hls_to_rgb(h, l, s)

        r_new_255 = int(r_new_norm * 255)
        g_new_255 = int(g_new_norm * 255)
        b_new_255 = int(b_new_norm * 255)

        return Color.from_rgb(r_new_255, g_new_255, b_new_255)

    def _get_base_char(self, x: int = 1) -> str:
        return "█"

    def render(self) -> RenderResult:
        start_color_str = self.app.theme_variables.get(
            "error-darken-3", self.app.theme_variables["accent"]
        )
        end_color_str = self.app.theme_variables.get(
            "error-lighten-3", self.app.theme_variables["error"]
        )

        start_color = Color.parse(start_color_str)
        end_color = Color.parse(end_color_str)

        bg_color = Color.parse(self.app.theme_variables["background"])

        interpolation_factor = self.lifetime / (self.age or 1)
        interpolation_factor = min(1.0, max(0.0, interpolation_factor))

        start_triplet = start_color.get_truecolor()
        end_triplet = end_color.get_truecolor()

        blended_triplet = blend_rgb(
            start_triplet, end_triplet, cross_fade=interpolation_factor
        )
        animated_base_color = Color.from_triplet(blended_triplet)

        text_line = MyText("")
        for i in range(self.m_size.width):
            effective_distance = i
            if self.direction.x < 0:
                effective_distance = self.m_size.width - 1 - i

            adjustment_factor = -(effective_distance / (self.m_size.width or 1)) * 0.3

            if self.adjust:
                adjustment_factor -= (randint(0, 10) / 10) * 0.35
            else:
                adjustment_factor -= (randint(0, 10) / 10) * 0.05

            adjusted_color = self._adjust_luminance_rich_color(
                animated_base_color, adjustment_factor
            )

            current_style = Style(color=adjusted_color, bgcolor=bg_color)
            text_line.append(self._get_base_char(i), style=current_style)

        return text_line


class TopLaser(Laser):
    type_name = "TopLaser"
    adjust = True

    def _get_base_char(self, x: int = 1) -> str:
        if x == self.m_size.width - 1:
            return " "
        anim = " 🬞🬏🬭🬓🬦🬖🬢🬱🬵"
        return choice(anim[: max(1, min(x, len(anim)))])


class MiddleLaser(Laser):
    type_name = "MiddleLaser"
    adjust = False

    def _get_base_char(self, x: int = 1) -> str:
        if x == self.m_size.width - 1:
            if self.direction.x > 0:
                anim = "🬰🬴🬛🬕🬲"
            else:
                anim = "🬰🬫🬨🬷🬸"
            return choice(anim)
        if x == 0:
            return "🬋"
        if x == 1:
            anim = "🬫🬩🬍" if self.direction.x > 0 else "🬛🬌🬚"
            return choice(anim)
        return choice("███████🬺🬻🬬🬝")


class BottomLaser(Laser):
    type_name = "BottomLaser"
    adjust = True

    def _get_base_char(self, x: int = 1) -> str:
        if x == self.m_size.width - 1:
            return " "
        anim = " 🬁🬀🬂🬄🬉🬈🬅🬆🬊"
        return choice(anim[: max(1, min(x, len(anim)))])
