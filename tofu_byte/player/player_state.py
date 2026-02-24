from typing import TYPE_CHECKING, List

from textual.geometry import Offset


from tofu_byte.objects.state import BaseState
from tofu_byte.tools.tools import Direction
from tofu_byte.game.events import EndGame

if TYPE_CHECKING:
    from tofu_byte.objects.state import BaseState
    from tofu_byte.tools.tools import Direction
    from tofu_byte.game.events import EndGame


def only_x(vector: Offset):
    return Offset(vector.x, 0)


def only_y(vector: Offset):
    return Offset(0, vector.y)


class PlayerState(BaseState):
    def __init__(
        self,
        player: "Player",
        max_frame: int,
        animation: List[str],
        frame: int = 0,
        direction: Offset = Offset(0, 0),
    ) -> None:
        super().__init__(max_frame, animation, frame, direction)
        self.player = player

    def update(self):
        pass

    def handle_input(self, directions_set: set[Direction]):
        offset_for_move = Offset(0, 0)
        if "l" in directions_set:
            offset_for_move += Offset(-1, 0)
        if "r" in directions_set:
            offset_for_move += Offset(1, 0)
        if offset_for_move != Offset(0, 0):
            self.player.velocity = only_y(self.player.velocity) + offset_for_move


class EditState(PlayerState):
    immortal: bool = True

    def __init__(self, player: "Player") -> None:
        super().__init__(player, 27, ["▄", "▃"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        pass

    def handle_input(self, directions_set: set[Direction]):
        pass


class StartState(PlayerState):
    immortal: bool = True

    def __init__(self, player: "Player") -> None:
        blocks = [
            "🬞",
            "🬏",
            "🬖",
            "🬢",
            "🬗",
            "🬤",
            "🬗",
            "🬤",
            "🬧",
            "🬔",
            "▐",
            "🬷",
            "🬻",
            "█",
            "🬎",
            "▀",
            "🮃",
            "🮂",
        ]
        super().__init__(player, len(blocks) * 2, blocks)

    def update(self):
        if self.animation_cycles_completed > 0:
            self.player.change_state(FallState(self.player))

    def handle_input(self, directions_set: set[Direction]):
        pass


class NoState(PlayerState):
    immortal: bool = True

    def __init__(self, player: "Player") -> None:
        super().__init__(player, 1, [" "])

    def update(self): ...

    def handle_input(self, directions_set: set[Direction]):
        pass

    def handle_input(self, directions_set: set[Direction]):
        pass


class DeadState(PlayerState):
    immortal: bool = True

    def __init__(self, player: "Player") -> None:
        super().__init__(player, 1, [" "])

    def update(self):
        self.player.post_message(EndGame())
        self.player.change_state(NoState(self.player))

    def handle_input(self, directions_set: set[Direction]):
        pass

    def handle_input(self, directions_set: set[Direction]):
        pass


class WinState(PlayerState):
    immortal: bool = True

    def __init__(self, player: "Player") -> None:
        super().__init__(player, 1, ["▀"])

    def update(self):
        self.player.post_message(EndGame(True))
        self.player.change_state(NoState(self.player))

    def handle_input(self, directions_set: set[Direction]):
        pass

    def handle_input(self, directions_set: set[Direction]):
        pass


class DyingState(PlayerState):
    immortal: bool = True

    def __init__(self, player: "Player") -> None:
        super().__init__(player, 15, ["▙", "▟", "▜", "▀", "▘", "▖"])

    def update(self):
        if self.animation_cycles_completed > 0:
            self.player.change_state(DeadState(self.player))

    def handle_input(self, directions_set: set[Direction]):
        pass

    def handle_input(self, directions_set: set[Direction]):
        pass


class StayState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 18, ["▂", "▃", "▄", "▃"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))
            return
        if "l" in directions_set or "r" in directions_set:
            self.player.change_state(MoveState(self.player))

        if "d" in directions_set:
            self.player.change_state(CrunchState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return


class CrunchState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 12, ["▁"] * 8 + ["▂"] * 4, direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))
            return
        if "l" in directions_set or "r" in directions_set:
            self.player.change_state(MoveState(self.player))

        if "d" in directions_set:
            self.player.change_state(CrunchState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return
        if self.animation_cycles_completed > 0:
            self.player.change_state(StayState(self.player))


class MoveState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 15, ["▂", "▄"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if not directions_set:
            self.player.change_state(StayState(self.player))
            return

        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return
        if self.player.velocity.x == 0:
            self.player.change_state(StayState(self.player))
            return


class PostFallState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 3, ["┃", "╻", "▂"], direction=Offset(0, 1))

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.player.change_state(PreJumpState(self.player))
            return
        if "l" in directions_set or "r" in directions_set:
            self.player.change_state(MoveState(self.player))

    def update(self):
        super().update()
        if not self.player.is_on_ground:
            self.player.change_state(FallState(self.player))
            return
        if self.animation_cycles_completed > 0:
            self.player.change_state(StayState(self.player))
            return


class FallState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 1, ["┃"], direction=Offset(0, 1))

    def update(self):
        super().update()
        if self.player.is_on_ground:
            self.player.change_state(PostFallState(self.player))


class PreJumpState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 6, ["▂", "╻", "┃"], direction=Offset(0, 0))

    def update(self):
        super().update()
        if self.animation_cycles_completed > 0:
            self.player.change_state(JumpState(self.player))


class JumpState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 4, ["┃"], direction=Offset(0, -1))

    def update(self):
        super().update()
        if self.animation_cycles_completed > 0:
            self.player.change_state(TopState(self.player))
        if self.player.is_on_roof is True:
            self.player.change_state(RoofState(self.player))


class TopState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 5, ["┃", "╹", "🮂", "🮂", "╹"], direction=Offset(0, 0))

    def update(self):
        super().update()
        if self.player.is_on_roof is True:
            self.player.change_state(RoofState(self.player))
            return
        if self.animation_cycles_completed > 0:
            self.player.change_state(FallState(self.player))


class RoofState(PlayerState):
    def __init__(self, player: "Player") -> None:
        super().__init__(player, 9, ["🮃", "▀"], direction=Offset(0, 0))
        self.can_roof_jump = 0
        self.should_fall_down = False

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        self.can_roof_jump = max(self.can_roof_jump - 1, 0)
        if "u" in directions_set:
            self.can_roof_jump = 2
        if "d" in directions_set:
            self.should_fall_down = True

    def update(self):
        super().update()
        if self.should_fall_down:
            self.player.change_state(FallState(self.player))
            return
        if self.player.is_on_roof is False:
            self.player.change_state(RoofCoyoteState(self.player, self.can_roof_jump))
            return


class RoofCoyoteState(PlayerState):
    def __init__(self, player: "Player", can_roof_jump: int = 0) -> None:
        super().__init__(player, 4 + can_roof_jump, ["🮃", "🮂"], direction=Offset(0, 0))
        self.can_roof_jump = can_roof_jump > 1
        self.should_fall_down = False
        assert can_roof_jump < 3

    def handle_input(self, directions_set: set[Direction]):
        super().handle_input(directions_set)
        if "u" in directions_set:
            self.can_roof_jump = True
        if "d" in directions_set:
            self.should_fall_down = True

    def update(self):
        super().update()
        if self.should_fall_down:
            self.player.change_state(FallState(self.player))
            return

        if not self.animation_cycles_completed > 0:
            return

        if self.player.is_on_roof is True:
            self.player.change_state(RoofState(self.player))
            return
        if self.can_roof_jump:
            self.player.change_state(JumpState(self.player))
            return
        self.player.change_state(FallState(self.player))
