from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button


class Footer(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Button("Go back")
