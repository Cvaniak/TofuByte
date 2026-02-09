from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from tofu_byte.objects.base_object import BaseObject
    from tofu_byte.player.player import Player


CLASS_REGISTRY: dict[str, type[BaseObject | Player]] = {}


def register(cls: type[BaseObject | Player]) -> type[BaseObject | Player]:
    CLASS_REGISTRY[cls.type_name] = cls
    return cls
