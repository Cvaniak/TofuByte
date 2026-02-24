from typing import List
from random import randint

from textual.geometry import Offset


class BaseState:
    max_frame: int
    animation: List[str]
    frame: int = 0
    direction: Offset = Offset(0, 0)
    immortal: bool = False
    animation_cycles_completed: int = 0

    def __init__(
        self,
        max_frame: int,
        animation: List[str],
        frame: int = 0,
        direction: Offset = Offset(0, 0),
    ) -> None:
        actual_len_animation = len(animation) if len(animation) > 0 else 1
        self.max_frame = max(max_frame, actual_len_animation)

        self.animation = animation
        self.frame = frame
        self.direction = direction
        self.animation_cycles_completed = 0

    def enter(self):
        pass

    def exit(self):
        pass

    def is_last_frame(self) -> bool:
        return self.frame == self.max_frame - 1

    def tick(self):
        if self.max_frame <= 1:
            self.frame = 0
            self.animation_cycles_completed += 1
        else:
            if (self.frame + 1) == self.max_frame:
                self.animation_cycles_completed += 1
            self.frame = (self.frame + 1) % self.max_frame

    def get_frame(self):
        if self.max_frame == 0:
            return self.animation[0] if self.animation else " "

        frame_idx = (self.frame * len(self.animation)) // self.max_frame
        frame_idx = min(frame_idx, len(self.animation) - 1)
        return self.animation[frame_idx]

    def get_random_frame(self):
        if self.animation:
            random_index = randint(0, len(self.animation) - 1)
            return self.animation[random_index]
        else:
            return " "


class RandomFrameState(BaseState):
    def __init__(
        self,
        max_frame: int,
        animation: List[str],
        frame: int = 0,
        direction: Offset = Offset(0, 0),
        probability: int = 2,
    ) -> None:
        super().__init__(max_frame, animation, frame, direction)
        self.last_frame = frame
        self.probability = probability

    def get_frame(self):
        if self.max_frame == 0:
            return self.animation[0] if self.animation else " "

        if randint(0, self.probability) == 0:
            self.last_frame = randint(0, len(self.animation) - 1)
        return self.animation[self.last_frame]
