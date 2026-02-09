from __future__ import annotations
from typing import Set, List, Optional
import threading
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from .input_manager import InputManager


class UnixInputManager(InputManager):
    def __init__(self) -> None:
        self.keys_pressed: Set[str] = set()
        self.lock: threading.Lock = threading.Lock()
        self.listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        if self.listener is not None:
            return
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self.listener.start()

    def stop(self) -> None:
        if self.listener is None:
            return
        self.listener.stop()
        self.listener = None

    def _get_key_str(self, key: Key | KeyCode | None) -> Optional[str]:
        if isinstance(key, KeyCode):
            return key.char
        if isinstance(key, Key):
            return key.name
        return None

    def _on_press(self, key: Key | KeyCode | None) -> None:
        key_str = self._get_key_str(key)
        if key_str is not None:
            with self.lock:
                self.keys_pressed.add(key_str)

    def _on_release(self, key: Key | KeyCode | None) -> None:
        key_str = self._get_key_str(key)
        if key_str is not None:
            with self.lock:
                self.keys_pressed.discard(key_str)

    def is_pressed(self, key_names: List[str]) -> bool:
        with self.lock:
            return any(k in self.keys_pressed for k in key_names)
