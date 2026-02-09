from typing import Literal
from rich.color import Color, blend_rgb
from .const import BACKGROUND

from textual.widget import Widget
from textual.message import Message


Direction = Literal["l", "r", "d", "u"]
# Offset = namedtuple("Offset", ["y", "x"])


def mn_mx(x, mn, mx):
    return min(max(x, mn), mx)


def calculate_blend(color, blend, sc_color=BACKGROUND):
    return Color.from_triplet(
        blend_rgb(
            sc_color.triplet,
            color.triplet,
            blend,
        )
    )


def calculate_light(y, x, color, lights, sc_color=BACKGROUND):
    if (y, x) in lights.light:
        # return Color.from_triplet(
        #     blend_rgb(
        #         sc_color.triplet,
        #         color.triplet,
        #         lights.light[(y, x)],
        #     )
        # )
        return color.c_blended[lights.light[(y, x)]]
    return sc_color.color


class DebugStatus(Message):
    def __init__(self, sender: Widget, mess):
        super().__init__(sender)
        self.mess = mess


def map_from_to(x, a, b, c, d):
    y = (x - a) / (b - a) * (d - c) + c
    if c > d:
        c, d = d, c
    y = mn_mx(y, c, d)
    return int(y)


if __name__ == "__main__":
    print(map_from_to(-5, 0, 30, 16, 0))
    print(map_from_to(5, 0, 30, 16, 0))
    print(map_from_to(55, 0, 30, 16, 0))
