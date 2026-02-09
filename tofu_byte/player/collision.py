from __future__ import annotations

from textual.geometry import Offset


from typing import TYPE_CHECKING, NamedTuple
from enum import Enum, auto

from tofu_byte.tools.tools import Direction


if TYPE_CHECKING:
    from tofu_byte.objects.base_object import BaseObject
    from tofu_byte.player.player import Player
    from tofu_byte.game.game import Scene


# TODO: Remove
def get_direction(direction: Offset) -> Direction:
    facing = Offset(direction.x, direction.y)

    if facing.x == 0:
        return "u" if facing.y > 0 else "d"
    # if only left or right
    if facing.y == 0:
        return "r" if facing.x > 0 else "l"

    return "r" if facing.x > 0 else "l"


class Side(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


class CollisionEvent(NamedTuple):
    player: Player
    obj: BaseObject
    side: Side
    target_pos: Offset


class Collision:
    collision_number = 0

    def __init__(self, mediator: Scene) -> None:
        self.mediator: Scene = mediator

    def _compute_side(self, v: Offset) -> Side:
        if abs(v.x) > abs(v.y):
            return Side.RIGHT if v.x > 0 else Side.LEFT
        else:
            return Side.BOTTOM if v.y > 0 else Side.TOP

    def _collision(
        self, player: Player, offset: Offset, velocity: Offset
    ) -> set[CollisionEvent]:
        new_pos = offset + velocity
        collisions: set[CollisionEvent] = set()

        self.collision_number += len(self.mediator.colliders)
        for obj in self.mediator.colliders:
            if obj.occupies_tile(new_pos):
                side = self._compute_side(velocity)
                collisions.add(CollisionEvent(player, obj, side, new_pos))
        return collisions

    def gather_collisions(self, player: Player) -> set[CollisionEvent]:
        v = player.velocity
        offset = player.offset

        collisions: set[CollisionEvent] = set()

        if v.y != 0:
            collisions |= self._collision(player, offset, Offset(0, v.y))
        else:
            collisions |= self._collision(player, offset, Offset(0, -1))
            collisions |= self._collision(player, offset, Offset(0, 1))

        if v.x != 0:
            collisions |= self._collision(player, offset, Offset(v.x, 0))

        if not collisions:
            collisions |= self._collision(player, offset, v)

        # TODO: Missing this, might cause problems in the future
        # collisions |= self._collision(player, offset, Offset(0, 0))

        return collisions
