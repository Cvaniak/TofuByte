from dataclasses import dataclass
from random import randint
from typing import List, Union

from textual.geometry import Offset


@dataclass
class Faze:
    frame: Union[int, None]
    max_frame: int
    animation: List[str]
    direction: Offset = Offset(0, 0)
    next_faze: Union["Faze", None] = None

    def get_frame(self):
        if self.frame is None:
            return self.animation[0]

        self.frame += 1
        if self.frame > self.max_frame:
            self.frame = 0

        frame = self.frame // (self.max_frame // len(self.animation) + 1)
        return self.animation[frame]

    def get_random_frame(self):
        if self.frame is None:
            return self.animation[0]

        self.frame = randint(0, self.max_frame)
        frame = self.frame // (self.max_frame // len(self.animation) + 1)
        return self.animation[frame]
