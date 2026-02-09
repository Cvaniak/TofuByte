from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class InputManager(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_pressed(self, key_names: List[str]) -> bool:
        raise NotImplementedError


def create_input_manager() -> InputManager:
    # It looked that pynput does not work with Windows but it seems to work now.
    from .unix_input_manager import UnixInputManager

    return UnixInputManager()
