from __future__ import annotations
from typing import Protocol, runtime_checkable, Set

from tofu_byte.tools.tools import Direction


@runtime_checkable
class InputConsumer(Protocol):
    def handle_input(self, directions_set: Set[Direction]) -> None: ...
