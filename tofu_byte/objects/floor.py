from typing import Any
from textual.app import RenderResult
from textual.geometry import Offset, Size

from tofu_byte.type_register import register
from tofu_byte.mystatic import MyText
from .base_object import BaseObject


@register
class Floor(BaseObject):
    type_name = "Floor"
    blocks = True
    triggers = True
    icon = ["🬰", "🬴", "🬸", "🬕", "🬲", " ", "🬨", "🬷", "▌", "▐", "🬂", "🬭", "█"]

    def __init__(
        self,
        pos: Offset = Offset(0, 0),
        size: Size = Size(4, 1),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(pos, size, *args, **kwargs)

    def default_colors(self) -> tuple[str, str]:
        background = self.app.theme_variables["surface"]
        color = self.app.theme_variables["surface-darken-3"]
        return background, color

    def render(self) -> RenderResult:
        style = self.set_colors()
        text = MyText(no_wrap=False, end="", style=style)
        if self.m_size.width == 1:
            text.append(self.icon[12] * self.m_size.height)

        if self.m_size.height == 1:
            text.append(
                "".join(
                    [self.icon[1], self.icon[0] * (self.m_size.width - 2), self.icon[2]]
                )
            )
        elif self.m_size.height == 2:
            text.append(
                "".join(
                    [
                        self.icon[3],
                        self.icon[10] * (self.m_size.width - 2),
                        self.icon[6],
                        "\n",
                    ]
                )
            )
            text.append(
                "".join(
                    [
                        self.icon[4],
                        self.icon[11] * (self.m_size.width - 2),
                        self.icon[7],
                    ]
                )
            )
        else:
            text.append(
                "".join(
                    [
                        self.icon[3],
                        self.icon[10] * (self.m_size.width - 2),
                        self.icon[6],
                        "\n",
                    ]
                )
            )
            for _ in range(self.m_size.height - 2):
                text.append(
                    "".join(
                        [
                            self.icon[8],
                            self.icon[5] * (self.m_size.width - 2),
                            self.icon[9],
                            "\n",
                        ]
                    )
                )
            text.append(
                "".join(
                    [
                        self.icon[4],
                        self.icon[11] * (self.m_size.width - 2),
                        self.icon[7],
                    ]
                )
            )
        return text
