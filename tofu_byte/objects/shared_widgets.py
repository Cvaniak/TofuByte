from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Static, Switch


class LabeledInput(Horizontal):
    def __init__(self, label: str, input_widget: Input) -> None:
        super().__init__()
        self.label_text = label
        self.input_widget = input_widget

    def compose(self) -> ComposeResult:
        yield Static(self.label_text, classes="label")
        yield self.input_widget


class LabeledSwitch(Horizontal):
    def __init__(self, label: str, swtich_widget: Switch) -> None:
        super().__init__()
        self.label_text = label
        self.switch_widget = swtich_widget

    def compose(self) -> ComposeResult:
        yield Static(self.label_text, classes="label")
        yield self.switch_widget
