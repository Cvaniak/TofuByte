from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from textual.app import ComposeResult, RenderResult
from textual.geometry import Size, Offset
from rich.style import Style
from textual.widgets import Button, Input


from tofu_byte.game.events import (
    ObjectResized,
)
from tofu_byte.objects.game_object import (
    GameObject,
    GameObjectParameters,
    MyText,
)
from tofu_byte.objects.state import BaseState
from tofu_byte.config import DEBUG
from tofu_byte.objects.shared_widgets import LabeledInput
from tofu_byte.game.collision_manager import Side

if TYPE_CHECKING:
    from tofu_byte.game.collision_manager import CollisionEvent


@dataclass
class BaseObjectParameters(GameObjectParameters):
    size: Size


class BaseObject(GameObject):
    type_name: str = "Undefined"
    blocks: bool = True
    triggers: bool = False
    icon: list[str] = [
        "🬰",
        "🬴",
        "🬸",
        "▆",
        "▗",
        "▖",
        "▛",
        "▜",
        "▟",
        "◢",
        "◣",
        "▐",
        "▌",
        "▬",
        "■",
    ]
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
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        anim_state: BaseState | None = None,
    ) -> None:
        super().__init__(
            pos=pos,
            size=size,
            editable=editable,
            layer_number=layer_number,
            layer_name=layer_name,
            name=name,
            id=id,
            classes=classes,
            anim_state=anim_state,
        )

    def occupies_tile(self, pos: Offset) -> bool:
        return (
            self.pos.x <= pos.x < self.pos.x + self.m_size.width
            and self.pos.y <= pos.y < self.pos.y + self.m_size.height
        )

    def blocks_movement(self, event: CollisionEvent) -> bool:
        return self.blocks

    def on_collision(self, event: CollisionEvent) -> None:
        if event.obj.type_name == "Player":
            self.last_collision_event = event

    def update_logic(self) -> None:
        if self.last_collision_event:
            pass

    def update_visuals(self):
        super().update_visuals()

    def set_colors(self) -> Style | None:
        dir_to_color = {
            Side.BOTTOM: "red",
            Side.TOP: "yellow",
            Side.RIGHT: "green",
            Side.LEFT: "blue",
        }
        if self.editable and self._focused_editable:
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

    def render(self) -> RenderResult:
        style = self.set_colors()
        return MyText(self.anim_state.get_frame(), style=style)

    def resize(self, delta: Offset, send_event: bool = True):
        if not self.resizeble:
            return
        self.set_size(self.m_size + delta, send_event)

    def set_size(self, new_size: Size, send_event: bool = True):
        self.m_size = new_size
        if send_event:
            self.post_message(ObjectResized(self.m_size))

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

    def validate_m_size(self, new_size: Size) -> Size:
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
        yield delete_button
        yield copy_button
        yield from super().edit_compose()
        if self.resizeble:
            yield LabeledInput("Width:", input_width)
            yield LabeledInput("Height:", input_height)

    def to_parameters(self) -> BaseObjectParameters:
        game_object_params = super().to_parameters()
        return BaseObjectParameters(
            type=game_object_params.type,
            pos=game_object_params.pos,
            layer_number=game_object_params.layer_number,
            size=self.m_size,
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> BaseObject:
        layer_number = data.get("layer_number", 1)
        return cls(
            pos=Offset(*data["pos"]),
            size=Size(*data["size"]),
            layer_number=layer_number,
        )

    def copy(self, **kwargs: Offset | Size | bool | int) -> Any:
        k: dict[str, Offset | Size | bool | int] = {
            "pos": self.pos,
            "size": self.m_size,
            "layer_number": self.layer_number,
            "editable": self.editable,
        }
        k.update(kwargs)
        return type(self)(**k)
