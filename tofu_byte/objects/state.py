from typing import TYPE_CHECKING, List, Union

from rich.style import Style
from textual.geometry import Offset

from tofu_byte.mystatic import MyText
from tofu_byte.tools.tools import Direction

if TYPE_CHECKING:
    from tofu_byte.player.player import Player


def only_x(vector: Offset):
    return Offset(vector.x, 0)


def only_y(vector: Offset):
    return Offset(0, vector.y)


class State:
    max_frame: int
    animation: List[str]
    frame: Union[int, None] = 0
    direction: Offset = Offset(0, 0)
    immortal: bool = False

    def __init__(
        self,
        player: "Player",
        max_frame: int,
        animation: List[str],
        frame: int = 0,
        direction: Offset = Offset(0, 0),
    ) -> None:
        self.player = player
        self.max_frame = max_frame
        self.animation = animation
        self.frame = frame
        self.direction = direction

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        self.player.offset += self.player.new_pos

    def handle_input(self, directions_set: set[Direction]):
        offset_for_move = Offset(0, 0)
        if "l" in directions_set:
            offset_for_move += Offset(-1, 0)
        if "r" in directions_set:
            offset_for_move += Offset(1, 0)
        if offset_for_move != Offset(0, 0):
            self.player.velocity = only_y(self.player.velocity) + offset_for_move

    def show(self, invert_color: int = False):
        bottom, top = self.player.color, self.player.color_sc
        if invert_color:
            bottom, top = self.player.color_sc, self.player.color

        new_frame = MyText(self.get_frame(), style=Style(color=bottom, bgcolor=top))
        if self.player.curr_frame != new_frame:
            self.player.update(new_frame)

    def get_frame(self):
        if self.frame is None:
            return self.animation[0]

        if self.frame >= self.max_frame:
            self.frame = 0

        frame = self.animation[(self.frame * len(self.animation)) // self.max_frame]
        self.frame += 1
        return frame
