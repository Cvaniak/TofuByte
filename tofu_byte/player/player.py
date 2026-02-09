from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from textual.app import ComposeResult
from textual.geometry import Offset
from typing import Any
from textual import events
from textual.widgets import Input


from tofu_byte.game.events import (
    EndGame,
    HpChange,
    PlayerClicked,
    PlayerMouseDown,
)
from tofu_byte.mystatic import GameObjectStatic
from tofu_byte.objects.state import State
from tofu_byte.screens.game_display import LabeledInput
from tofu_byte.tools.const import BACKGROUND
from tofu_byte.mystatic import MyText
from tofu_byte.type_register import register

from ..tools.loggerr import get_textlog

from .collision import Collision, CollisionEvent, Side
from ..objects.base_object import BaseObject

from ..tools.tools import Direction

from typing import Set

directions = {"l": Offset(-1, 0), "r": Offset(1, 0)}


class MouseState(Enum):
    MOUSE_DOWN = auto()
    MOUSE_UP_AFTER_DRAGGING = auto()
    MOUSE_DRAGGING = auto()
    NO_MOUSE = auto()


@dataclass
class PlayerParameters:
    type: str
    pos: Offset
    layer_number: int


class EditState(State):
    immortal: bool = True

    def __init__(self, player: Player) -> None:
        super().__init__(player, 27, ["▄", "▃"], direction=Offset(0, 1))


class StartState(State):
    immortal: bool = True

    def __init__(self, player: Player) -> None:
        blocks = [
            "🬞",
            "🬏",
            "🬖",
            "🬢",
            "🬗",
            "🬤",
            "🬗",
            "🬤",
            "🬧",
            "🬔",
            "▐",
            "🬷",
            "🬻",
            "█",
            "🬎",
            "▀",
            "🮃",
            "🮂",
        ]
        super().__init__(player, len(blocks) * 2, blocks)

    def update(self):
        if self.frame == self.max_frame:
            self.player.change_state(FallState(self.player))


class NoState(State):
    immortal: bool = True

    def __init__(self, player: Player) -> None:
        super().__init__(player, 1, [" "])

    def update(self): ...


class DeadState(State):
    immortal: bool = True

    def __init__(self, player: Player) -> None:
        super().__init__(player, 1, [" "])

    def update(self):
        self.player.post_message(EndGame())
        self.player.change_state(NoState(self.player))


class WinState(State):
    immortal: bool = True

    def __init__(self, player: Player) -> None:
        super().__init__(player, 1, ["▀"])

    def update(self):
        self.player.post_message(EndGame(True))
        self.player.change_state(NoState(self.player))


class DyingState(State):
    immortal: bool = True

    def __init__(self, player: Player) -> None:
        super().__init__(player, 15, ["▙", "▟", "▜", "▀", "▘", "▖"])

    def update(self):
        if self.frame == self.max_frame:
            self.player.change_state(DeadState(self.player))


class StayState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 18, ["▂", "▃", "▄", "▃"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))
            return
        if "l" in directions_set or "r" in directions_set:
            self.player.change_state(MoveState(self.player))

        if "d" in directions_set:
            self.player.change_state(CrunchState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return


class CrunchState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 12, ["▁"] * 8 + ["▂"] * 4, direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))
            return
        if "l" in directions_set or "r" in directions_set:
            self.player.change_state(MoveState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return
        if self.frame == self.max_frame:
            self.player.change_state(StayState(self.player))


class MoveState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 15, ["▂", "▄"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if not directions_set:
            self.player.change_state(StayState(self.player))
            return

        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
        if self.player.velocity.x == 0:
            self.player.change_state(StayState(self.player))


class PostFallState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 2, ["╻", "▂"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))
            return
        if "l" in directions_set or "r" in directions_set:
            self.player.change_state(MoveState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return
        if self.frame == self.max_frame:
            self.player.change_state(StayState(self.player))
            return


class FallState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 1, ["┃"], direction=Offset(0, 1))

    def update(self):
        super().update()
        if self.player.is_on_ground:
            self.player.change_state(PostFallState(self.player))


class PreJumpState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 6, ["▂", "╻", "┃"], direction=Offset(0, 0))
        # super().__init__(player, 15, ["▂", "╻", "┃"], direction=Offset(0, 0)) # previous version

    def update(self):
        super().update()
        if self.frame == self.max_frame:
            self.player.change_state(JumpState(self.player))


class JumpState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 4, ["┃"], direction=Offset(0, -1))

    def update(self):
        super().update()
        if self.frame == self.max_frame:
            self.player.change_state(TopState(self.player))
        if self.player.is_on_roof is True:
            self.player.change_state(RoofState(self.player))


class TopState(State):
    def __init__(self, player: Player) -> None:
        super().__init__(player, 5, ["┃", "╹", "🮂", "🮂", "╹"], direction=Offset(0, 0))
        # super().__init__(player, 5, ["▂"], direction=Offset(0, 0)) # previous version

    def update(self):
        super().update()
        if self.player.is_on_roof is True:
            self.player.change_state(RoofState(self.player))
            return
        if self.frame == self.max_frame:
            self.player.change_state(FallState(self.player))


class RoofState(State):
    def __init__(self, player: Player) -> None:
        # super().__init__(player, 12, ["▀", "🮃"], direction=Offset(0, 0)) # previous version
        super().__init__(player, 9, ["🮃", "▀"], direction=Offset(0, 0))
        self.can_roof_jump = 0
        self.should_fall_down = False

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        self.can_roof_jump = max(self.can_roof_jump - 1, 0)
        if "u" in directions_set:
            self.can_roof_jump = 2
        if "d" in directions_set:
            self.should_fall_down = True

    def update(self):
        super().update()
        if self.should_fall_down:
            self.player.change_state(FallState(self.player))
            return
        # if self.can_roof_jump is True and self.player.is_on_roof is True:
        #     self.player.change_state(RoofCoyoteState(self.player))
        if self.player.is_on_roof is False:
            self.player.change_state(RoofCoyoteState(self.player, self.can_roof_jump))
            return


class RoofCoyoteState(State):
    def __init__(self, player: Player, can_roof_jump: int = 0) -> None:
        # super().__init__(player, 15, ["🮆", "▀", "🮃"], direction=Offset(0, 0))  # previous version
        super().__init__(player, 4 + can_roof_jump, ["🮃", "🮂"], direction=Offset(0, 0))
        self.can_roof_jump = can_roof_jump > 1
        self.should_fall_down = False
        assert can_roof_jump < 3

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.can_roof_jump = True
        if "d" in directions_set:
            self.should_fall_down = True

    def update(self):
        super().update()
        if self.should_fall_down:
            self.player.change_state(FallState(self.player))
            return

        if self.frame != self.max_frame:
            return

        if self.player.is_on_roof is True:
            self.player.change_state(RoofState(self.player))
            return
        if self.can_roof_jump:
            self.player.change_state(JumpState(self.player))
            return
        self.player.change_state(FallState(self.player))


@register
class Player(GameObjectStatic):
    type_name = "Player"

    def __init__(
        self,
        start_pos: Offset = Offset(1, 1),
        layer_number: int = 2,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.layer_number = layer_number
        self.should_remove = False
        self.editable = False
        self.curr_frame = MyText()

        self.coliders: Set[BaseObject] = set()
        self.collision_directions: set[Direction] = set()
        self.effects_list = []

        self.direction_set: Set[Direction] = set()
        self.move_blocker: int = 0
        self.hue = 0
        self.starting_pos = start_pos

        self.collision = Collision(self)
        self.set_player(start_pos)
        self.styles.layer = f"a{self.layer_number}{self.type_name}"

        self.on_roof = False
        self.color = "red"
        self.color_sc = BACKGROUND
        # self.styles.color = self.color
        # self.styles.background = self.color_sc
        self.textlog = get_textlog()
        self.mouse_state = MouseState.NO_MOUSE

    def set_player(self, pos: Offset) -> None:
        self.end_facing: Offset = Offset(0, 0)
        self.facing: Offset = Offset(0, 0)
        self.prev_facing: Offset = Offset(0, 0)
        self.pos: Offset = pos
        self.alive = True
        self.collision_directions = set()
        self.offset = pos
        self.state: State = StartState(self)
        self.velocity: Offset = Offset(0, 0)
        self.is_on_ground = False
        self.is_on_roof = False
        self.foo = Offset(0, 0)

    def update_clear_values(self):
        self.is_on_ground = False
        self.is_on_roof = False
        self.facing = Offset(0, 0)
        self.velocity = Offset(0, 0) + self.state.direction

    def change_state(self, new_state: State):
        self.state = new_state

    def handle_input(self, directions_set: set[Direction]):
        self.state.handle_input(directions_set)

    def update_states(self):
        self.state.update()

    @property
    def new_pos(self) -> Offset:
        return self.velocity

    def reset(self):
        self.set_player(self.starting_pos)

    def on_collision(self, event: CollisionEvent):
        side = event.side

        if side == Side.BOTTOM:
            self.is_on_ground = True
            self.velocity = Offset(self.velocity.x, 0)

        elif side == Side.TOP:
            self.is_on_roof = True
            self.velocity = Offset(self.velocity.x, 0)

        elif side == Side.LEFT or side == Side.RIGHT:
            self.velocity = Offset(0, self.velocity.y)

    def show(self) -> None:
        self.state.show()

    def damage(self) -> None:
        if not self.state.immortal:
            self.change_state(DyingState(self))
            self.post_message(HpChange(-1))

    def win(self) -> None:
        self.change_state(WinState(self))

    def change_color(self) -> None:
        vars = self.app.theme_variables
        self.hue = (self.hue + 50) % 1000
        self.color = vars.get("player-color", self.app.theme_variables.get("accent"))
        self.color_sc = vars["background"]

    # def my_update(self, content):
    #     self.__content = content
    #     self.__visual = visualize(self, content, markup=self._render_markup)

    def edit_state(self):
        self.state = EditState(self)

    async def on_enter(self, event: events.Enter):
        self.is_entered = True

    async def on_leave(self, event: events.Leave):
        self.is_entered = False

    async def on_click(self, event: events.Click):
        if self.mouse_state not in [
            MouseState.MOUSE_DRAGGING,
            MouseState.MOUSE_UP_AFTER_DRAGGING,
        ]:
            self.post_message(PlayerClicked(event, self))

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse()
        event.stop()
        self.mouse_state = MouseState.MOUSE_DOWN
        self.post_message(PlayerMouseDown(event, self))

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        self.capture_mouse(False)
        if self.mouse_state == MouseState.MOUSE_DRAGGING:
            self.mouse_state = MouseState.MOUSE_UP_AFTER_DRAGGING
        else:
            self.mouse_state = MouseState.NO_MOUSE

    def move(self, delta: Offset):
        self.pos = self.pos + delta
        self.styles.offset = Offset(self.pos.x, self.pos.y)
        self.mouse_state = MouseState.MOUSE_DRAGGING

    def resize(self, delta: Offset, send_event: bool = True): ...

    def edit_compose(self) -> ComposeResult:
        input_layer = Input(
            value=str(self.layer_number), type="number", id="object_layer_number"
        )
        yield LabeledInput("Layer number:", input_layer)

    def focused_editable(self, is_focused_editable: bool):
        self._focused_editable = is_focused_editable
        if is_focused_editable:
            self.add_class("focused_editable")
        else:
            self.remove_class("focused_editable")

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Player:
        layer_number = data.get("layer_number", 1)
        return cls(Offset(*data["pos"]), layer_number=layer_number)

    def to_parameters(self) -> PlayerParameters:
        return PlayerParameters(self.type_name, self.pos, self.layer_number)
