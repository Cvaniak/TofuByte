from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Static


class LabeledInput(Horizontal):
    def __init__(self, label: str, input_widget: Input) -> None:
        super().__init__()
        self.label_text = label
        self.input_widget = input_widget

    def compose(self) -> ComposeResult:
        yield Static(self.label_text, classes="label")
        yield self.input_widget
