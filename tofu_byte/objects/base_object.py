from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Concatenate, ParamSpec, TypeVar
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.events import MouseMove
from textual.geometry import Size, Offset
from textual.reactive import reactive
from rich.style import Style
from textual.widgets import Button, Input, Static
from textual import events


from tofu_byte.game.events import (
    LayerNumberChange,
    ObjectClicked,
    ObjectMouseDown,
    ObjectResized,
)
from tofu_byte.mystatic import GameObjectStatic
from tofu_byte.config import DEBUG
from tofu_byte.mystatic import MyText
from tofu_byte.objects.shared_widgets import LabeledInput
from tofu_byte.player.collision import Side

if TYPE_CHECKING:
    from tofu_byte.player.collision import CollisionEvent


class SceneStatic(Static): ...


class StaticHorizontal(Horizontal): ...


class BaseObject2(GameObjectStatic):
    def __init__(self) -> None: ...


@dataclass
class BaseObjectParameters:
    type: str
    pos: Offset
    size: Size
    layer_number: int


class MouseState(Enum):
    MOUSE_DOWN = auto()
    MOUSE_UP_AFTER_DRAGGING = auto()
    MOUSE_DRAGGING = auto()
    NO_MOUSE = auto()


P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")  # the class type (self)


def _editable(
    func: Callable[Concatenate[T, P], R],
) -> Callable[Concatenate[T, P], R | None]:
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R | None:
        if not getattr(self, "editable", False):
            return None
        return func(self, *args, **kwargs)

    return wrapper


class BaseObject(GameObjectStatic):
    type_name = "Undefined"
    m_size = reactive(Size(0, 0), recompose=True)
    blocks = True
    triggers = False
    editable = reactive(False)
    layer_number = reactive(2)
    icon = ["🬰", "🬴", "🬸", "▆", "▗", "▖", "▛", "▜", "▟", "◢", "◣", "▐", "▌", "▬", "■"]
    resizeble: bool = True
    min_size: Size = Size(1, 1)
    max_size: Size = Size(-1, -1)

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(4, 1),
        editable: bool = False,
        layer_number: int = 1,
        layer_name: str | None = None,
    ) -> None:
        super().__init__(markup=False)
        self.should_remove = False
        self.pos = pos
        self.m_size = Size(size.width, size.height)
        self.layer_number = layer_number
        self.last_collision_event: CollisionEvent | None = None
        self.curr_frame = MyText("")

        self.styles.offset = Offset(self.pos.x, self.pos.y)
        if layer_name is not None:
            self.styles.layer = layer_name
        else:
            self.set_layer_number()

        self.editable = editable
        self.mouse_state = MouseState.NO_MOUSE

    def render(self) -> RenderResult:
        return ""

    def set_layer_number(self):
        self.styles.layer = f"a{self.layer_number}{self.type_name}{id(self)}"
        self.post_message(LayerNumberChange())

    def watch_layer_number(self):
        self.set_layer_number()

    def watch_m_size(self, new_size: Size):
        self.styles.width = new_size.width
        self.styles.height = new_size.height

    def focused_editable(self, is_focused_editable: bool):
        self._focused_editable = is_focused_editable
        if is_focused_editable:
            self.add_class("focused_editable")
        else:
            self.remove_class("focused_editable")

    def occupies_tile(self, pos: Offset) -> bool:
        return (
            self.pos.x <= pos.x < self.pos.x + self.m_size.width
            and self.pos.y <= pos.y < self.pos.y + self.m_size.height
        )

    def blocks_movement(self, event: CollisionEvent) -> bool:
        return bool(self.blocks)

    def on_collision(self, event: CollisionEvent) -> None:
        self.last_collision_event = event

    def update_clear_values(self):
        self.last_collision_event = None

    def reload(self):
        if self.last_collision_event:
            ...

        new_frame = self.render()
        if new_frame != self.curr_frame:
            self.curr_frame = new_frame
            self.update(new_frame)

    # def my_update(self, content):
    #     self.__content = content
    #     self.__visual = visualize(self, content, markup=self._render_markup)

    def set_colors(self) -> Style | None:
        dir_to_color = {
            Side.BOTTOM: "red",
            Side.TOP: "yellow",
            Side.RIGHT: "green",
            Side.LEFT: "blue",
        }
        if self.editable and self.focused_editable:
            return None
        elif self.last_collision_event:
            if DEBUG["contact_dir"]:
                color = dir_to_color[self.last_collision_event.side]
                return Style(color=color)
        return None

    def default_colors(self) -> tuple[str, str]:
        background = self.app.theme_variables["surface"]
        color = self.app.theme_variables["surface-darken-3"]
        return background, color

    # ========================

    @_editable
    async def on_enter(self, event: events.Enter):
        self.is_entered = True

    @_editable
    async def on_leave(self, event: events.Leave):
        self.is_entered = False

    @_editable
    async def on_mouse_down(self, event: events.MouseDown) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse()
        event.stop()
        self.mouse_state = MouseState.MOUSE_DOWN
        self.post_message(ObjectMouseDown(event, self))

    @_editable
    async def on_mouse_up(self, event: events.MouseUp) -> None:
        self.capture_mouse(False)
        if self.mouse_state == MouseState.MOUSE_DRAGGING:
            self.mouse_state = MouseState.MOUSE_UP_AFTER_DRAGGING
        else:
            self.mouse_state = MouseState.NO_MOUSE

    @_editable
    async def on_click(self, event: events.Click) -> None:
        if self.mouse_state not in [
            MouseState.MOUSE_DRAGGING,
            MouseState.MOUSE_UP_AFTER_DRAGGING,
        ]:
            self.post_message(ObjectClicked(event, self))
        # self.capture_mouse(False)

    def move(self, delta: Offset):
        self.pos = self.pos + delta
        self.styles.offset = Offset(self.pos.x, self.pos.y)
        self.mouse_state = MouseState.MOUSE_DRAGGING

    def resize(self, delta: Offset, send_event: bool = True):
        if not self.resizeble:
            return
        self.set_size(self.m_size + delta, send_event)

    def set_size(self, new_size: Size, send_event: bool = True):
        self.m_size = new_size
        if send_event:
            self.post_message(ObjectResized(self.m_size))

    @_editable
    async def on_mouse_move(self, event: MouseMove):
        pass

    def validate_m_size_width(self, new_width: int) -> int:
        if self.min_size.width != -1:
            new_width = max(new_width, self.min_size.width)
        if self.max_size.width != -1:
            new_width = min(new_width, self.max_size.width)
        return new_width

    def validate_m_size_height(self, new_height: int) -> int:
        if self.min_size.height != -1:
            new_height = max(new_height, self.min_size.height)

        if self.max_size.height != -1:
            new_height = min(new_height, self.max_size.height)
        return new_height

    def validate_m_size(self, new_size: Size):
        return Size(
            self.validate_m_size_width(new_size.width),
            self.validate_m_size_height(new_size.height),
        )

    def edit_compose(self) -> ComposeResult:
        delete_button = Button("Delete Object", id="delete_object", variant="error")
        copy_button = Button("Copy Object", id="copy_object", variant="warning")
        input_width = Input(
            value=str(self.m_size.width), type="number", id="object_width"
        )
        input_height = Input(
            value=str(self.m_size.height), type="number", id="object_height"
        )
        input_layer = Input(
            value=str(self.layer_number), type="number", id="object_layer_number"
        )
        yield delete_button
        yield copy_button
        if self.resizeble:
            yield LabeledInput("Width:", input_width)
            yield LabeledInput("Height:", input_height)
        yield LabeledInput("Layer number:", input_layer)

    # ========================

    def to_parameters(self) -> BaseObjectParameters:
        return BaseObjectParameters(
            self.type_name, self.pos, self.size, self.layer_number
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> BaseObject:
        layer_number = data.get("layer_number", 1)
        return cls(Offset(*data["pos"]), Size(*data["size"]), layer_number=layer_number)

    def copy(self, **kwargs: Offset | Size | bool | int):
        k: dict[str, Offset | Size | bool | int] = {
            "pos": self.pos,
            "size": self.size,
            "layer_number": self.layer_number,
            "editable": self.editable,
        }
        k.update(kwargs)
        return type(self)(**k)
