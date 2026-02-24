from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from tofu_byte.objects.game_object import GameObject


CLASS_REGISTRY: dict[str, type[GameObject]] = {}


def register(cls: type[GameObject]) -> type[GameObject]:
    CLASS_REGISTRY[cls.type_name] = cls
    return cls
