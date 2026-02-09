from __future__ import annotations

from typing import Any
from textual.geometry import Offset, Size

from tofu_byte.objects.base_object import BaseObject
from tofu_byte.player.collision import CollisionEvent
from tofu_byte.type_register import register


@register
class KillingBondary(BaseObject):
    type_name = "KillingBondary"
    triggers = True

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(1, 1),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pos, size, layer_number=0, *args, **kwargs)

    def occupies_tile(self, pos: Offset) -> bool:
        return not super().occupies_tile(pos)

    def on_collision(self, event: CollisionEvent) -> None:
        event.player.damage()

    def watch_editable(self, new_value: bool):
        if new_value:
            self.display = True
        else:
            self.display = False
