from __future__ import annotations

from typing import TYPE_CHECKING
from textual import events
from textual.geometry import Size
from textual.message import Message


if TYPE_CHECKING:
    from tofu_byte.objects.base_object import BaseObject
    from tofu_byte.player.player import Player


class HpChange(Message):
    def __init__(self, val: int) -> None:
        super().__init__()
        self.val = val


class PointCollected(Message):
    def __init__(self, val: int = 1) -> None:
        super().__init__()
        self.val = val


class EndBallCollected(Message):
    def __init__(self) -> None:
        super().__init__()


class StatsClear(Message):
    def __init__(self, hp: int = 1, max_points: int = 1) -> None:
        super().__init__()
        self.hp = hp
        self.max_points = max_points


class DisplayClicked(Message):
    def __init__(self, event: events.MouseDown) -> None:
        super().__init__()
        self.event = event


class DisplayMouseHover(Message):
    def __init__(self, event: events.MouseMove) -> None:
        super().__init__()
        self.event = event


class ObjectClicked(Message):
    def __init__(self, event: events.Click, object: BaseObject) -> None:
        super().__init__()
        self.event = event
        self.object = object


class PlayerClicked(Message):
    def __init__(self, event: events.Click, object: Player) -> None:
        super().__init__()
        self.event = event
        self.object = object


class ObjectMouseDown(Message):
    def __init__(self, event: events.MouseDown, object: BaseObject) -> None:
        super().__init__()
        self.event = event
        self.object = object


class PlayerMouseDown(Message):
    def __init__(self, event: events.MouseDown, object: Player) -> None:
        super().__init__()
        self.event = event
        self.object = object


class EndGame(Message):
    def __init__(self, won: bool = False) -> None:
        super().__init__()
        self.won = won


class ObjectResized(Message):
    def __init__(self, new_size: Size) -> None:
        super().__init__()
        self.new_size = new_size


class LayerNumberChange(Message):
    def __init__(self) -> None:
        super().__init__()
