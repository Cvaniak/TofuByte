from __future__ import annotations
from typing import Any, List
from textual.geometry import Offset, Size
from textual.app import RenderResult, ComposeResult
from rich.style import Style
from textual.widgets import Input, Switch
from tofu_byte.objects.shared_widgets import LabeledInput, LabeledSwitch
from dataclasses import dataclass

from tofu_byte.type_register import register
from tofu_byte.objects.game_object import MyText
from tofu_byte.game.collision_manager import CollisionEvent
from tofu_byte.objects.state import BaseState
from .base_object import BaseObject, BaseObjectParameters


@dataclass
class EnemyParameters(BaseObjectParameters):
    move_interval: int
    direction: int


WS = "\u2800"


class EnemyState(BaseState):
    def __init__(
        self,
        enemy: Enemy,
        max_frame: int,
        animation: List[str],
        direction: Offset = Offset(0, 0),
    ) -> None:
        super().__init__(max_frame, animation, direction=direction)
        self.enemy = enemy


class EnemyPatrolState(EnemyState):
    def __init__(self, enemy: Enemy) -> None:
        animation = [
            "▄▄██",
            "▁▁██)",
            f"{WS}{WS}██)",
            f"{WS}{WS}▆▆)",
            f"{WS}{WS}▄▄)",
            f"{WS}{WS}🬦🬓)",
            f"{WS}{WS}▐▌)",
            "🬞🬏▐▌",
            "🬦🬓▐▌",
            "▐▌▐▌",
            "▐▌🬉🬄",
            "▐▌🬁🬀",
            f"▐▌{WS}{WS}",
            f"▀▀{WS}{WS}",
            f"▀▀{WS}{WS}",
        ]
        animation += list(reversed(animation))[1:]
        super().__init__(
            enemy,
            len(animation) * 2,
            animation,
        )

    def update(self) -> None:
        if self.frame % self.enemy.move_interval == 0:
            self.enemy.patrol_step()


@register
class Enemy(BaseObject):
    type_name = "Enemy"
    blocks: bool = True
    triggers: bool = True
    resizeble: bool = False

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(2, 2),
        move_interval: int = 10,
        direction: int = 1,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pos, size, *args, **kwargs)
        self.move_interval = move_interval
        self.move_direction = direction  # 1 for right, -1 for left
        self.anim_state = EnemyPatrolState(self)
        self.game_world_manager = None

    def patrol_step(self) -> None:
        if not self.game_world_manager:
            return

        cm = self.game_world_manager.collision_manager

        next_x = self.pos.x + self.move_direction
        wall_objs = cm.get_objects_at(
            self.pos.x + self.m_size.width
            if self.move_direction > 0
            else self.pos.x - 1,
            self.pos.y,
            1,
            self.m_size.height,
        )
        has_wall = any(o.blocks for o in wall_objs if o is not self)

        check_x = next_x + (self.m_size.width - 1 if self.move_direction > 0 else 0)
        floor_objs = cm.get_objects_at(check_x, self.pos.y + self.m_size.height, 1, 1)
        has_floor = any(o.blocks for o in floor_objs)

        if has_wall or not has_floor:
            self.move_direction *= -1
        else:
            old_pos = self.pos
            self.pos = Offset(next_x, self.pos.y)
            cm.update_object_position(self, old_pos, self.pos)

    def update_logic(self) -> None:
        self.anim_state.update()

    def on_collision(self, event: CollisionEvent) -> None:
        if event.obj.type_name == "Player":
            event.obj.damage()

    def render(self) -> RenderResult:
        color = self.app.theme_variables["error"]
        bg = self.app.theme_variables["background"]
        style = Style(color=color, bgcolor=bg)
        frame = self.anim_state.get_frame()
        return MyText(frame, style=style)

    def edit_compose(self) -> ComposeResult:
        yield from super().edit_compose()
        yield LabeledInput(
            "Move Interval:",
            Input(
                value=str(self.move_interval),
                type="number",
                id="enemy_move_interval",
            ),
        )
        yield LabeledSwitch(
            "Direction X:",
            Switch(
                value=self.move_direction > 0,
                id="enemy_direction",
            ),
        )

    def to_parameters(self) -> EnemyParameters:
        game_object_params = super().to_parameters()
        return EnemyParameters(
            type=game_object_params.type,
            pos=game_object_params.pos,
            layer_number=game_object_params.layer_number,
            size=game_object_params.size,
            move_interval=self.move_interval,
            direction=self.move_direction,
        )

    def copy(self, **kwargs) -> Enemy:
        k: dict[str, Any] = {
            "pos": self.pos,
            "size": self.m_size,
            "layer_number": self.layer_number,
            "editable": self.editable,
            "move_interval": self.move_interval,
            "direction": self.move_direction,
        }
        k.update(kwargs)
        return type(self)(**k)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Enemy:
        layer_number = data.get("layer_number", 1)
        return cls(
            pos=Offset(*data["pos"]),
            size=Size(*data.get("size", [2, 2])),
            layer_number=layer_number,
            move_interval=data.get("move_interval", 5),
            direction=data.get("direction", 1),
        )
