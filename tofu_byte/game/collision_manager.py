from __future__ import annotations
from collections import defaultdict
from typing import TYPE_CHECKING
from enum import Enum, auto
from dataclasses import dataclass

from textual.geometry import Offset

if TYPE_CHECKING:
    from tofu_byte.objects.game_object import GameObject
    from tofu_byte.objects.base_object import BaseObject


class Side(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass
class CollisionEvent:
    mover: GameObject
    obj: GameObject
    side: Side
    target_pos: Offset


class CollisionManager:
    def __init__(self) -> None:
        self.grid: dict[tuple[int, int], list[BaseObject]] = defaultdict(list)
        self.resolved_pairs: set[tuple[int, int]] = set()

    def prepare_frame(self, all_objects: set[GameObject]) -> None:
        self.resolved_pairs.clear()
        self.rebuild_grid(all_objects)

    def rebuild_grid(self, all_objects: set[GameObject]) -> None:
        self.grid.clear()
        for obj in all_objects:
            if obj.blocks or obj.triggers:
                for cell in obj.get_occupied_cells():
                    self.grid[cell].append(obj)  # type: ignore

    def get_objects_at(
        self, x: int, y: int, width: int, height: int
    ) -> set[BaseObject]:
        found: set[BaseObject] = set()
        for i in range(x, x + width):
            for j in range(y, y + height):
                if (i, j) in self.grid:
                    for obj in self.grid[(i, j)]:
                        found.add(obj)
        return found

    def update_object_position(
        self, obj: GameObject, old_pos: Offset, new_pos: Offset
    ) -> None:
        if not (obj.blocks or obj.triggers):
            return

        old_cells = set()
        x, y = old_pos.x, old_pos.y
        w, h = obj.m_size.width, obj.m_size.height
        for i in range(x, x + w):
            for j in range(y, y + h):
                old_cells.add((i, j))

        new_cells = set()
        nx, ny = new_pos.x, new_pos.y
        for i in range(nx, nx + w):
            for j in range(ny, ny + h):
                new_cells.add((i, j))

        to_remove = old_cells - new_cells
        to_add = new_cells - old_cells

        for cell in to_remove:
            if cell in self.grid:
                if obj in self.grid[cell]:  # type: ignore
                    self.grid[cell].remove(obj)  # type: ignore
                if not self.grid[cell]:
                    del self.grid[cell]

        for cell in to_add:
            self.grid[cell].append(obj)  # type: ignore

    def notify_collision(
        self, mover: GameObject, other: BaseObject, side: Side, target_pos: Offset
    ) -> None:
        pair_id = tuple(sorted((id(mover), id(other))))
        if pair_id in self.resolved_pairs:
            return

        event_mover = CollisionEvent(mover, other, side, target_pos)
        mover.on_collision(event_mover)

        opposite_side = side
        if side == Side.TOP:
            opposite_side = Side.BOTTOM
        elif side == Side.BOTTOM:
            opposite_side = Side.TOP
        elif side == Side.LEFT:
            opposite_side = Side.RIGHT
        elif side == Side.RIGHT:
            opposite_side = Side.LEFT

        event_other = CollisionEvent(other, mover, opposite_side, target_pos)  # type: ignore
        other.on_collision(event_other)

        self.resolved_pairs.add(pair_id)  # type: ignore

    def move_and_collide(self, mover: GameObject, velocity: Offset) -> None:
        # X Axis Pass First
        steps_x = abs(velocity.x)
        dir_x = 1 if velocity.x > 0 else -1

        for _ in range(steps_x):
            target_x = mover.pos.x + dir_x
            potential_collisions = self.get_objects_at(
                target_x, mover.pos.y, mover.m_size.width, mover.m_size.height
            )

            can_move_x = True
            for other in potential_collisions:
                if other is mover:
                    continue

                side = Side.RIGHT if dir_x > 0 else Side.LEFT
                self.notify_collision(mover, other, side, Offset(target_x, mover.pos.y))

                if other.blocks:
                    can_move_x = False

            if can_move_x:
                old_pos = mover.pos
                mover.pos = Offset(target_x, mover.pos.y)
                self.update_object_position(mover, old_pos, mover.pos)
            else:
                break

        # Y Axis Pass Second
        steps_y = abs(velocity.y)
        dir_y = 1 if velocity.y > 0 else -1

        for _ in range(steps_y):
            target_y = mover.pos.y + dir_y
            potential_collisions = self.get_objects_at(
                mover.pos.x, target_y, mover.m_size.width, mover.m_size.height
            )

            can_move_y = True
            for other in potential_collisions:
                if other is mover:
                    continue

                side = Side.BOTTOM if dir_y > 0 else Side.TOP
                self.notify_collision(mover, other, side, Offset(mover.pos.x, target_y))

                if other.blocks:
                    can_move_y = False

            if can_move_y:
                old_pos = mover.pos
                mover.pos = Offset(mover.pos.x, target_y)
                self.update_object_position(mover, old_pos, mover.pos)
            else:
                break

    def _probe_direction(self, mover: GameObject, offset: Offset, side: Side) -> None:
        probe_pos = mover.pos + offset
        objects = self.get_objects_at(
            probe_pos.x, probe_pos.y, mover.m_size.width, mover.m_size.height
        )
        for other in objects:
            if other is mover:
                continue
            self.notify_collision(mover, other, side, mover.pos)

    def check_surroundings(self, mover: GameObject) -> None:
        if mover.type_name != "Player":
            return

        # Check current position for triggers/overlaps
        self._probe_direction(mover, Offset(0, 0), Side.BOTTOM)

        self._probe_direction(mover, Offset(0, -1), Side.TOP)
        self._probe_direction(mover, Offset(0, 1), Side.BOTTOM)
        self._probe_direction(mover, Offset(-1, 0), Side.LEFT)
        self._probe_direction(mover, Offset(1, 0), Side.RIGHT)
