from __future__ import annotations

from textual.app import RenderResult

from tofu_byte.player.collision import CollisionEvent, Side
from tofu_byte.type_register import register
from tofu_byte.mystatic import MyText

from .base_object import BaseObject

from typing import Any
from textual.geometry import Offset, Size


@register
class Spikes(BaseObject):
    type_name = "Spikes"
    blocks: bool = True
    triggers: bool = True
    icon = ["◢", "◣"]
    max_size = Size(-1, 1)
    contact_direction = Side.BOTTOM

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(4, 1),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pos, size, *args, **kwargs)

    def render(self) -> RenderResult:
        style = self.set_colors()
        return MyText(
            f"{self.icon[0]}{self.icon[1]}" * (self.m_size.width // 2),
            style=style,
        )

    def default_colors(self) -> tuple[str, str]:
        color = self.app.theme_variables["warning"]
        background = self.app.theme_variables["background"]
        return color, background

    def occupies_dead_zone(self, pos: Offset):
        return (
            self.pos.x + 1 <= pos.x < self.pos.x + self.m_size.width - 1
            and self.pos.y - 1 <= pos.y < self.pos.y
        )

    def occupies_spike_zone(self, pos: Offset):
        return (
            self.pos.x <= pos.x < self.pos.x + self.m_size.width
            and self.pos.y <= pos.y < self.pos.y + self.m_size.height
        )

    def occupies_tile(self, pos: Offset) -> bool:
        return self.occupies_spike_zone(pos) or self.occupies_dead_zone(pos)

    def blocks_movement(self, event: CollisionEvent) -> bool:
        if self.occupies_dead_zone(event.target_pos):
            return False
        return bool(self.blocks)

    def on_collision(self, event: CollisionEvent) -> None:
        super().on_collision(event)

        if self.occupies_dead_zone(event.player.offset):
            event.player.damage()
            return
        if self.occupies_spike_zone(event.player.offset):
            event.player.damage()
            return
        if self.occupies_spike_zone(event.target_pos) and event.side in [
            self.contact_direction
        ]:
            event.player.damage()
            return


@register
class SpikesDown(Spikes):
    type_name = "SpikesDown"
    icon = ["◥", "◤"]
    contact_direction = Side.TOP

    def occupies_dead_zone(self, pos: Offset):
        return (
            self.pos.x + 1 <= pos.x < self.pos.x + self.m_size.width - 1
            and self.pos.y <= pos.y < self.pos.y - 1
        )
