from __future__ import annotations
from dataclasses import dataclass

from textual.app import ComposeResult, RenderResult
from textual.geometry import Offset, Size
from textual.widgets import Input

from tofu_byte.type_register import register
from tofu_byte.mystatic import MyText
from .base_object import BaseObject, LabeledInput
from typing import Any


@dataclass
class TextObjectParameters:
    type: str
    pos: Offset
    size: Size
    layer_number: int
    text_value: str


@register
class FloatingText(BaseObject):
    type_name = "Text"
    blocks: bool = False
    triggers: bool = False
    resizeble: bool = True

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(4, 1),
        text_value: str = "Text",
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(pos, size, *args, **kwargs)
        self.text_value = text_value
        self.update(self.render())

    def default_colors(self) -> tuple[str, str]:
        color = self.app.theme_variables["success"]
        background = self.app.theme_variables["background"]
        return color, background

    def render(self) -> RenderResult:
        style = self.set_colors()
        return MyText(self.text_value, style=style)

    def edit_compose(self) -> ComposeResult:
        text_input = Input(self.text_value, id="object_text")
        yield from super().edit_compose()
        yield LabeledInput("Text value", text_input)

    def watch_text_value(self, new_value: str):
        self.resize(Size(len(new_value), self.m_size.height))

    def to_parameters(self) -> TextObjectParameters:
        return TextObjectParameters(
            self.type_name, self.pos, self.size, self.layer_number, self.text_value
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> BaseObject:
        layer_number = data.get("layer_number", 1)
        text_value = data.get("text_value", "Lorem ipsum")
        return cls(
            Offset(*data["pos"]),
            Size(*data["size"]),
            text_value=text_value,
            layer_number=layer_number,
        )

    def copy(self, **kwargs: Offset | Size | bool | int | str):
        k: dict[str, Offset | Size | bool | int | str] = {
            "pos": self.pos,
            "size": self.size,
            "layer_number": self.layer_number,
            "editable": self.editable,
            "text_value": self.text_value,
        }
        k.update(kwargs)
        return type(self)(**k)
