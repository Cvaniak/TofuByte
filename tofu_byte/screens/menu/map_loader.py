from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast, NamedTuple
from pathlib import Path
import importlib.resources as res

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from tofu_byte.config import user_dir
from tofu_byte.screens.const import LOAD_MAP
from tofu_byte.mystatic import PrimaryScreenTitle
from tofu_byte.screens.screens import MenuScreenBase
from tofu_byte.tools.map_utils import create_empty_map


user_maps_dir = user_dir / "maps"
user_maps_dir.mkdir(parents=True, exist_ok=True)


class MyPath(NamedTuple):
    path: Path
    builtin: bool
    is_dir: bool = False


class NewMapData(NamedTuple):
    map_name: str
    authors: list[str]


@dataclass
class MapChain:
    current_index: int
    maps: list[Path]

    def current_map(self) -> Path:
        return self.maps[self.current_index]

    def next_map(self) -> Path | None:
        if not self.has_next_map():
            return None
        self.current_index += 1
        return self.current_map()

    def has_next_map(self):
        return self.current_index + 1 < len(self.maps)


USER_MAPS_PACKAGE = MyPath(user_maps_dir, False, True)


def user_map(name: str) -> Path:
    return Path(user_maps_dir / f"{name}.json")


def list_builtin_root() -> list[MyPath]:
    items: list[MyPath] = []
    packages: list[MyPath] = []
    custom: list[MyPath] = []

    # builtin packages / maps
    for t in res.files("tofu_byte.maps").iterdir():
        if t.is_dir() and t.name != "__pycache__":
            packages.append(MyPath(Path(t), True, True))
        elif t.name.endswith(".json"):
            with res.as_file(t) as rp:
                items.append(MyPath(Path(rp), True))

    if any(user_maps_dir.iterdir()):
        custom.append(USER_MAPS_PACKAGE)

    return (
        sorted(packages, key=lambda x: x.path.name)
        + sorted(items, key=lambda x: x.path.name)
        + custom
    )


def list_maps_in(path: Path) -> list[MyPath]:
    items: list[MyPath] = []
    packages: list[MyPath] = []

    for p in path.iterdir():
        if p.is_dir() and p.name != "__pycache__":
            packages.append(MyPath(Path(p), path != user_maps_dir, True))
        elif p.suffix == ".json":
            items.append(MyPath(Path(p), path != user_maps_dir))

    return sorted(packages, key=lambda x: x.path.name) + sorted(
        items, key=lambda x: x.path.name
    )


class MapButton(Button):
    def __init__(self, path: MyPath, *args: Any, **kwargs: Any):
        self.is_dir: bool = path.is_dir
        self.path: Path = path.path

        text = path.path.stem
        if text.split("_")[0].isnumeric():
            text = text.partition("_")[2].replace("_", " ")
        if path.builtin:
            text = "⭐ " + text

        kwargs["variant"] = "warning" if path.is_dir else "primary"
        super().__init__(text, *args, **kwargs)


class CreateNewMapScreen(ModalScreen[NewMapData]):
    BINDINGS = [
        Binding("enter", "create", "Create"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Provide name of new map", id="question_name"),
            Input("name_of_the_map", id="map_name"),
            Label("Provide authors (seperated by comma)", id="question_authors"),
            Input("name_of_the_map", id="authors"),
            Button("Create", variant="success", id="create"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog",
        )

    def _submit(self) -> None:
        input_widget = self.query_one("#map_name", Input)
        name = input_widget.value.strip()

        if not name:
            input_widget.add_class("error")
            self.notify("Map name can not be empty.", severity="warning")
            return

        target = user_map(name)
        if target.exists():
            self.notify(f"Map {target} already exists!", severity="error")
            input_widget.add_class("error")
            return

        input_widget_authors = self.query_one("#authors", Input)
        authors = input_widget_authors.value.strip()

        if not authors:
            input_widget.add_class("error")
            self.notify("Authors can not be empty", severity="warning")
            return
        authors_list: list[str] = authors.split(",")

        self.dismiss(NewMapData(name, authors_list))

    def on_input_submitted(self) -> None:
        self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        else:
            self._submit()


class MapLoader(MenuScreenBase[MapChain]):
    def __init__(self, start_path: Path | None = None) -> None:
        super().__init__()
        self.current_path: Path | None = start_path

    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(LOAD_MAP)
        with VerticalScroll():
            pass
        with Container():
            yield Button("Back", id="back", variant="error")

    def on_mount(self) -> None:
        self.update()

    def update(self) -> None:
        scroll = self.query_one(VerticalScroll)
        scroll.remove_children()

        if self.current_path is None:
            items = list_builtin_root()
        else:
            items = list_maps_in(self.current_path)

        for p in items:
            scroll.mount(MapButton(p, classes="map_button"))

    @on(Button.Pressed, ".map_button")
    async def handle_press(self, event: Button.Pressed) -> None:
        button = cast(MapButton, event.button)

        if button.is_dir:
            self.current_path = button.path
            self.update()
            return

        if self.current_path is not None:
            map_chain = [x.path for x in list_maps_in(self.current_path)]
            index = map_chain.index(Path(button.path))
            self.dismiss(MapChain(index, map_chain))
        else:
            self.dismiss(MapChain(0, [Path(button.path)]))

    def action_go_back(self):
        if self.current_path is not None:
            self.current_path = None
            self.update()
        else:
            self.app.pop_screen()


class MapEditor(MapLoader):
    def compose(self) -> ComposeResult:
        with Container():
            yield PrimaryScreenTitle(LOAD_MAP)
        with Container():
            yield Button("Create Map", id="create_map", variant="success")
        with VerticalScroll():
            pass
        with Container():
            yield Button("Back", id="back", variant="error")

    def update(self) -> None:
        scroll = self.query_one(VerticalScroll)
        scroll.remove_children()

        if self.current_path is None:
            items = list_builtin_root()
        else:
            items = list_maps_in(self.current_path)

        for p in items:
            scroll.mount(MapButton(p, classes="map_button"))

    def _return_new_map(self, new_map_data: NewMapData) -> None:
        new_map_file = user_map(new_map_data.map_name)
        create_empty_map(new_map_file, new_map_data.authors)
        self.dismiss(MapChain(0, [new_map_file]))

    @on(Button.Pressed, "#create_map")
    async def create_map_button(self, event: Button.Pressed) -> None:
        self.app.push_screen(CreateNewMapScreen(), self._return_new_map)
