from __future__ import annotations
from typing import Any, List
from dataclasses import dataclass
from textual.geometry import Offset, Size
from textual.app import RenderResult, ComposeResult
from textual.widgets import Input, Switch
from tofu_byte.objects.shared_widgets import LabeledInput, LabeledSwitch
from rich.style import Style

from tofu_byte.type_register import register
from tofu_byte.objects.game_object import MyText
from tofu_byte.objects.state import BaseState
from .base_object import BaseObject, BaseObjectParameters
from .laser import TopLaser, MiddleLaser, BottomLaser


@dataclass
class TouretParameters(BaseObjectParameters):
    shoot_interval: int
    laser_lifetime: int
    laser_distance: int
    direction: Offset


class TouretState(BaseState):
    def __init__(
        self,
        touret: Touret,
        max_frame: int,
        animation: List[str],
        direction: Offset = Offset(0, 0),
    ) -> None:
        super().__init__(max_frame, animation, direction=direction)
        self.touret = touret


class TouretIdleState(TouretState):
    def __init__(self, touret: Touret) -> None:
        super().__init__(
            touret,
            touret.shoot_interval,
            ["🬺🬋 ▎╲"] if touret.direction.x == 1 else ["🬋🬻╱🮇"],
        )

    def update(self) -> None:
        if self.animation_cycles_completed > 0:
            self.touret.change_state(TouretShootingState(self.touret))


class TouretShootingState(TouretState):
    def __init__(self, touret: Touret) -> None:
        super().__init__(
            touret,
            touret.laser_lifetime,
            ["🬺🬋 ▎╲"] if touret.direction.x == 1 else ["🬋🬻╱🮇"],
        )

    def enter(self) -> None:
        if not (
            hasattr(self.touret, "game_world_manager")
            and self.touret.game_world_manager
        ):
            return

        world = self.touret.game_world_manager
        cm = world.collision_manager

        max_w = self.touret.laser_distance
        height = 3

        if self.touret.direction.x > 0:
            start_x = self.touret.pos.x + self.touret.m_size.width
            step = 1
        else:
            start_x = self.touret.pos.x - 1
            step = -1

        start_y = self.touret.pos.y - 1

        for y_off in range(height):
            actual_w = 0
            check_y = start_y + y_off

            for w in range(1, max_w + 1):
                check_x = start_x + (w - 1) * step
                objs = cm.get_objects_at(check_x, check_y, 1, 1)
                if any(
                    o.blocks for o in objs if o.type_name not in ["Player", "Touret"]
                ):
                    break
                actual_w = w

            if actual_w > 0:
                if self.touret.direction.x > 0:
                    laser_pos = Offset(start_x, check_y)
                else:
                    laser_pos = Offset(start_x - actual_w + 1, check_y)

                if y_off == 0:
                    laser_cls = TopLaser
                elif y_off == 1:
                    laser_cls = MiddleLaser
                else:
                    laser_cls = BottomLaser

                laser = laser_cls(
                    pos=laser_pos,
                    size=Size(actual_w, 1),
                    lifetime=self.touret.laser_lifetime,
                    direction=self.touret.direction,
                )
                world.add_object_to_dicts(laser)
                world.mediator.mount_drawable(laser)

    def update(self) -> None:
        if self.animation_cycles_completed > 0:
            self.touret.change_state(TouretIdleState(self.touret))


@register
class Touret(BaseObject):
    type_name = "Touret"
    blocks: bool = True
    triggers: bool = True
    resizeble: bool = False

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(2, 2),
        shoot_interval: int = 30,
        laser_lifetime: int = 30,
        laser_distance: int = 15,
        direction: Offset = Offset(1, 0),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pos, size, *args, **kwargs)
        self.shoot_interval = shoot_interval
        self.laser_lifetime = laser_lifetime
        self.laser_distance = laser_distance
        self.direction = direction
        self.anim_state = TouretIdleState(self)
        self.game_world_manager = None

    def change_state(self, new_state: TouretState) -> None:
        self.anim_state.exit()
        self.anim_state = new_state
        self.anim_state.enter()

    def update_logic(self) -> None:
        self.anim_state.update()

    def render(self) -> RenderResult:
        color = self.app.theme_variables["warning"]
        bg = self.app.theme_variables["background"]
        style = Style(color=color, bgcolor=bg)
        frame = self.anim_state.get_frame()

        return MyText(f"{frame}", style=style)

    def edit_compose(self) -> ComposeResult:
        yield from super().edit_compose()
        yield LabeledInput(
            "Shoot Interval:",
            Input(
                value=str(self.shoot_interval),
                type="number",
                id="touret_shoot_interval",
            ),
        )
        yield LabeledInput(
            "Laser Lifetime:",
            Input(
                value=str(self.laser_lifetime),
                type="number",
                id="touret_laser_lifetime",
            ),
        )
        yield LabeledInput(
            "Laser Distance:",
            Input(
                value=str(self.laser_distance),
                type="number",
                id="touret_laser_distance",
            ),
        )
        yield LabeledSwitch(
            "Direction X:",
            Switch(
                value=self.direction.x > 0,
                id="touret_direction_x",
            ),
        )

    def to_parameters(self) -> TouretParameters:
        game_object_params = super().to_parameters()
        return TouretParameters(
            type=game_object_params.type,
            pos=game_object_params.pos,
            layer_number=game_object_params.layer_number,
            size=game_object_params.size,
            shoot_interval=self.shoot_interval,
            laser_lifetime=self.laser_lifetime,
            laser_distance=self.laser_distance,
            direction=self.direction,
        )

    def copy(self, **kwargs) -> Touret:
        k: dict[str, Any] = {
            "pos": self.pos,
            "size": self.m_size,
            "layer_number": self.layer_number,
            "editable": self.editable,
            "shoot_interval": self.shoot_interval,
            "laser_lifetime": self.laser_lifetime,
            "laser_distance": self.laser_distance,
            "direction": self.direction,
        }
        k.update(kwargs)
        return type(self)(**k)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Touret:
        layer_number = data.get("layer_number", 1)
        dir_data = data.get("direction", [1, 0])
        return cls(
            pos=Offset(*data["pos"]),
            size=Size(*data.get("size", [2, 2])),
            layer_number=layer_number,
            shoot_interval=data.get("shoot_interval", 30),
            laser_lifetime=data.get("laser_lifetime", 30),
            laser_distance=data.get("laser_distance", 15),
            direction=Offset(*dir_data),
        )
