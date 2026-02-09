from __future__ import annotations
from typing import Generic, TypeVar

from textual import on
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.events import ScreenResume, ScreenSuspend
from textual.screen import Screen
from textual.widgets import Button

from tofu_byte.mystatic import ScreenTitle


map_file = "map.pxl"

ResultType = TypeVar("ResultType")


class MenuScreenBase(Generic[ResultType], Screen[ResultType]):
    AUTO_FOCUS = "Button"
    ...
    BINDINGS = [
        Binding("tab,j,s,down", "app.focus_next", "Focus Next", show=False),
        Binding("shift+tab,k,w,up", "app.focus_previous", "Focus Previous", show=False),
        Binding("escape", "go_back", "Go Back", show=False),
    ]

    def action_go_back(self):
        self.app.pop_screen()

    @on(ScreenSuspend)
    def on_screen_suspend(self):
        try:
            screen_titles = self.query(ScreenTitle)
            for screen_title in screen_titles:
                screen_title.stop_gradient()
        except NoMatches:
            ...

    @on(ScreenResume)
    def on_screen_resume(self):
        try:
            screen_titles = self.query(ScreenTitle)
            for screen_title in screen_titles:
                screen_title.start_gradient()
        except NoMatches:
            ...

    @on(Button.Pressed, "#back")
    def on_back_button(self):
        self.action_go_back()
