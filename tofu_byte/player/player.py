from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from textual.app import ComposeResult, RenderResult
from textual.geometry import Offset
from textual import events
from rich.style import Style


from tofu_byte.game.events import (
    HpChange,
    PlayerClicked,
    PlayerMouseDown,
)
from tofu_byte.objects.game_object import (
    GameObject,
    editable_only,
    MouseState,
    GameObjectParameters,
    MyText,
)
from tofu_byte.player.player_state import (
    PlayerState,
    StartState,
    EditState,
    DyingState,
    WinState,
)
from tofu_byte.tools.const import BACKGROUND
from tofu_byte.type_register import register

from ..tools.loggerr import get_textlog

from tofu_byte.game.collision_manager import CollisionEvent, Side
from ..tools.tools import Direction

from typing import Set

directions = {"l": Offset(-1, 0), "r": Offset(1, 0)}


@dataclass
class PlayerParameters(GameObjectParameters):
    pass


@register
class Player(GameObject):
    type_name: str = "Player"
    blocks: bool = True
    triggers: bool = True

    def __init__(
        self,
        start_pos: Offset = Offset(1, 1),
        layer_number: int = 2,
        editable: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            pos=start_pos,
            layer_number=layer_number,
            editable=editable,
            name=name,
            id=id,
            classes=classes,
            anim_state=None,
            **kwargs,
        )
        self.should_remove = False
        self.curr_frame: MyText = MyText()

        self.coliders: Set[GameObject] = set()
        self.collision_directions: set[Direction] = set()
        self.effects_list = []

        self.direction_set: Set[Direction] = set()
        self.move_blocker: int = 0
        self.hue = 0
        self.starting_pos = start_pos

        self.set_player(start_pos)

        self.on_roof = False
        self.color = "red"
        self.color_sc = BACKGROUND
        self.textlog = get_textlog()

    def set_player(self, pos: Offset) -> None:
        self.end_facing: Offset = Offset(0, 0)
        self.facing: Offset = Offset(0, 0)
        self.prev_facing: Offset = Offset(0, 0)
        self.pos: Offset = pos
        self.alive = True
        self.collision_directions = set()
        self.anim_state: PlayerState = StartState(self)
        self.is_on_ground = False
        self.is_on_roof = False
        self.foo = Offset(0, 0)

    def update_clear_values(self) -> None:
        super().update_clear_values()
        self.is_on_ground = False
        self.is_on_roof = False
        self.facing = Offset(0, 0)
        self.velocity = Offset(0, 0) + self.anim_state.direction

    def update_logic(self) -> None:
        self.anim_state.update()

    def change_state(self, new_state: PlayerState) -> None:
        self.anim_state = new_state

    def handle_input(self, directions_set: set[Direction]) -> None:
        self.anim_state.handle_input(directions_set)

    @property
    def new_pos(self) -> Offset:
        return self.velocity

    def reset(self) -> None:
        self.set_player(self.starting_pos)

    def on_collision(self, event: CollisionEvent) -> None:
        if not event.obj.blocks:
            return

        side = event.side

        if side == Side.BOTTOM:
            self.is_on_ground = True
            self.velocity = Offset(self.velocity.x, 0)

        elif side == Side.TOP:
            self.is_on_roof = True
            self.velocity = Offset(self.velocity.x, 0)

        elif side == Side.LEFT or side == Side.RIGHT:
            self.velocity = Offset(0, self.velocity.y)

    def render(self) -> RenderResult:
        bottom, top = self.color, self.color_sc
        style = Style(color=bottom, bgcolor=top)
        return MyText(self.anim_state.get_frame(), style=style)

    def update_visuals(self) -> None:
        self.change_color()
        super().update_visuals()

    def damage(self) -> None:
        if not self.anim_state.immortal:
            self.change_state(DyingState(self))
            self.post_message(HpChange(-1))

    def win(self) -> None:
        self.change_state(WinState(self))

    def change_color(self) -> None:
        vars = self.app.theme_variables
        self.hue = (self.hue + 50) % 1000
        self.color = vars.get("player-color", self.app.theme_variables.get("accent"))
        self.color_sc = vars["background"]

    def edit_state(self) -> None:
        self.anim_state = EditState(self)

    @editable_only
    async def on_click(self, event: events.Click) -> None:
        await super().on_click(event)
        if self.mouse_state not in [
            MouseState.MOUSE_DRAGGING,
            MouseState.MOUSE_UP_AFTER_DRAGGING,
        ]:
            self.post_message(PlayerClicked(event, self))

    @editable_only
    async def on_mouse_down(self, event: events.MouseDown) -> None:
        await super().on_mouse_down(event)
        self.post_message(PlayerMouseDown(event, self))

    def edit_compose(self) -> ComposeResult:
        yield from super().edit_compose()

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Player:
        layer_number = data.get("layer_number", 1)
        return cls(start_pos=Offset(*data["pos"]), layer_number=layer_number)

    def to_parameters(self) -> PlayerParameters:
        game_object_params = super().to_parameters()
        return PlayerParameters(
            type=game_object_params.type,
            pos=game_object_params.pos,
            layer_number=game_object_params.layer_number,
        )
