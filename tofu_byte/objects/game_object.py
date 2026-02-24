from __future__ import annotations

from tofu_byte.objects.state import BaseState

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Concatenate, ParamSpec, TypeVar
from textual.app import ComposeResult, RenderResult
from textual.geometry import Size, Offset
from textual.reactive import reactive
from textual.widgets import Input, Static
from textual import events
from textual.message_pump import MessagePump
from rich.text import Text
from tofu_byte.game.events import (
    LayerNumberChange,
    ObjectMouseDown,
    ObjectClicked,
)

if TYPE_CHECKING:
    from tofu_byte.game.collision_manager import CollisionEvent


T = TypeVar("T", bound="GameObject")

P = ParamSpec("P")

R = TypeVar("R")


def editable_only(
    func: Callable[Concatenate[T, P], R],
) -> Callable[Concatenate[T, P], R | None]:
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R | None:
        if not self.editable:
            return None
        return func(self, *args, **kwargs)

    return wrapper


class MouseState(Enum):
    MOUSE_DOWN = auto()
    MOUSE_UP_AFTER_DRAGGING = auto()
    MOUSE_DRAGGING = auto()
    NO_MOUSE = auto()


@dataclass
class GameObjectParameters:
    type: str
    pos: Offset
    layer_number: int


class MyText(Text):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MyText):
            return NotImplemented
        return (
            self.plain == other.plain
            and self._spans == other._spans
            and self.style == other.style
        )


class GameObject(Static, MessagePump):
    type_name: str = "GameObject"

    pos = reactive(Offset(0, 0))
    velocity = reactive(Offset(0, 0))
    m_size = reactive(Size(0, 0), recompose=True)
    layer_number = reactive(1)
    editable = reactive(False)
    blocks: bool = False
    triggers: bool = False
    anim_state: BaseState

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(1, 1),
        layer_number: int = 1,
        editable: bool = False,
        layer_name: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        anim_state: BaseState | None = None,
    ) -> None:
        super().__init__(markup=False, name=name, id=id, classes=classes)

        self.should_remove: bool = False
        self.pos = pos
        self.m_size = size
        self.layer_number = layer_number
        self.editable = editable
        self.last_collision_event: CollisionEvent | None = None
        self.curr_frame: MyText | str = ""
        self.anim_state = (
            anim_state
            if anim_state is not None
            else BaseState(max_frame=1, animation=["?"])
        )

        self.mouse_state = MouseState.NO_MOUSE

        self._focused_editable: bool = False
        self.is_entered: bool = False

        if layer_name is not None:
            self.styles.layer = layer_name
        else:
            self.set_layer_number()

    def watch_pos(self, new_pos: Offset) -> None:
        self.styles.offset = new_pos

    def render(self) -> RenderResult:
        return self.curr_frame

    def set_layer_number(self) -> None:
        self.styles.layer = f"a{self.layer_number}{self.type_name}-{id(self)}"
        self.post_message(LayerNumberChange(self.layer_number))

    def watch_layer_number(self, new_layer_number: int) -> None:
        self.set_layer_number()

    def watch_m_size(self, new_size: Size) -> None:
        self.styles.width = new_size.width
        self.styles.height = new_size.height

    def focused_editable(self, is_focused_editable: bool) -> None:
        self._focused_editable = is_focused_editable
        if is_focused_editable:
            self.add_class("focused_editable")
        else:
            self.remove_class("focused_editable")

    def move(self, delta: Offset) -> None:
        self.pos = self.pos + delta
        self.mouse_state = MouseState.MOUSE_DRAGGING

    def update_clear_values(self) -> None:
        self.last_collision_event = None

    def update_visuals(self) -> None:
        new_frame = self.render()
        if new_frame != self.curr_frame:
            self.curr_frame = new_frame
            self.update(new_frame)

    def update_logic(self) -> None:
        pass

    @editable_only
    async def on_enter(self, event: events.Enter) -> None:
        self.is_entered = True

    @editable_only
    async def on_leave(self, event: events.Leave) -> None:
        self.is_entered = False

    @editable_only
    async def on_mouse_down(self, event: events.MouseDown) -> None:
        if self.app is not None and self.app.mouse_captured is None:
            self.capture_mouse()
        event.stop()
        self.mouse_state = MouseState.MOUSE_DOWN
        self.post_message(ObjectMouseDown(event, self))

    @editable_only
    async def on_mouse_up(self, event: events.MouseUp) -> None:
        self.capture_mouse(False)
        if self.mouse_state == MouseState.MOUSE_DRAGGING:
            self.mouse_state = MouseState.MOUSE_UP_AFTER_DRAGGING
        else:
            self.mouse_state = MouseState.NO_MOUSE

    @editable_only
    async def on_click(self, event: events.Click) -> None:
        if self.mouse_state not in [
            MouseState.MOUSE_DRAGGING,
            MouseState.MOUSE_UP_AFTER_DRAGGING,
        ]:
            self.post_message(ObjectClicked(event, self))

    @editable_only
    async def on_mouse_move(self, event: events.MouseMove) -> None:
        pass

    def edit_compose(self) -> ComposeResult:
        from tofu_byte.objects.shared_widgets import LabeledInput

        input_layer = Input(
            value=str(self.layer_number), type="number", id="object_layer_number"
        )
        yield LabeledInput("Layer number:", input_layer)

    def to_parameters(self) -> GameObjectParameters:
        return GameObjectParameters(
            type=self.type_name,
            pos=self.pos,
            layer_number=self.layer_number,
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> T:
        layer_number = data.get("layer_number", 1)
        return cls(
            pos=Offset(*data["pos"]),
            size=Size(*data["size"]),
            layer_number=layer_number,
        )

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameObject):
            return NotImplemented
        return id(self) == id(other)

    @property
    def grid_rect(self) -> tuple[int, int, int, int]:
        return (self.pos.x, self.pos.y, self.m_size.width, self.m_size.height)

    def get_occupied_cells(self) -> set[tuple[int, int]]:
        cells = set()
        x, y, w, h = self.grid_rect
        for i in range(x, x + w):
            for j in range(y, y + h):
                cells.add((i, j))
        return cells

    def on_collision(self, event: Any) -> None:
        pass
