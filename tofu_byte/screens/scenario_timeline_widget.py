from textual.widgets import Static, ListItem, ListView
from textual.app import ComposeResult
from textual.containers import Vertical
from rich.text import Text
from typing import List, Set
from tofu_byte.tools.tools import Direction


class ScenarioTimelineWidget(Static):
    def __init__(self, timeline: List[Set[Direction]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.timeline = timeline
        self.list_view = ListView(id="timeline-list")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Timeline", classes="debug-title")
            yield self.list_view

    def on_mount(self) -> None:
        self.rebuild_list()

    def rebuild_list(self) -> None:
        items = []

        items.append(ListItem(Static(Text("00: Initial State", style="bold cyan"))))

        for i, inputs in enumerate(self.timeline):
            input_str = ", ".join(sorted(inputs)) if inputs else "-"
            text = Text()
            text.append(f"{(i + 1):02}: ", style="bold cyan")
            text.append(input_str, style="yellow")
            items.append(ListItem(Static(text)))

        self.list_view.clear()
        self.list_view.extend(items)

    def highlight_step(self, index: int) -> None:
        if 0 <= index < len(self.list_view.children):
            self.list_view.index = index
            item = self.list_view.children[index]
            self.list_view.scroll_to_region(item.region, animate=False, center=True)
