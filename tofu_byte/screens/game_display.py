from __future__ import annotations
from dataclasses import asdict
import pathlib
from typing import TYPE_CHECKING, Optional

from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import (
    Grid,
    Horizontal,
    ScrollableContainer,
    Vertical,
)
from textual.css.query import NoMatches
from textual.events import Click, MouseEvent, MouseMove, ScreenResume, ScreenSuspend
from textual.geometry import Offset, Size
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Input, Label, ListItem, ListView, Static
from tofu_byte.config import DEBUG, GAME_VERSION, should_check_input_system
from tofu_byte.game.events import (
    DisplayClicked,
    DisplayMouseHover,
    EndBallCollected,
    EndGame,
    HpChange,
    LayerNumberChange,
    ObjectClicked,
    ObjectMouseDown,
    ObjectResized,
    PlayerClicked,
    PlayerMouseDown,
    PointCollected,
)
from tofu_byte.game.input_manager import InputManager, create_input_manager
from tofu_byte.objects.base_object import BaseObject
from tofu_byte.objects.shared_widgets import LabeledInput
from tofu_byte.player.player import Player
from tofu_byte.screens.menu.end_screen import EditEndScreen, EndScreen

from tofu_byte.game.display import Display

from tofu_byte.screens.menu.map_loader import MapChain
from tofu_byte.screens.screens import MenuScreenBase
from tofu_byte.tools.loggerr import get_textlog
from tofu_byte.game.game import Editor, Game
from textual import on

from tofu_byte.mystatic import GameObjectStatic, LifePoints, Points, TimeDisplay
import json

from tofu_byte.type_register import CLASS_REGISTRY

if TYPE_CHECKING:
    from tofu_byte.objects.map import MapConfigValues


class SceneStatic(Static): ...


class StaticHorizontal(Horizontal): ...


class FooterCustom(ScrollableContainer, can_focus=False, can_focus_children=False):
    ALLOW_SELECT = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fps = Static("123")

    def compose(self) -> ComposeResult:
        yield self.fps


class GameObjectListItem(ListItem):
    def __init__(self, game_object) -> None:
        super().__init__()
        self.game_object = game_object

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.game_object
            yield Static(f" {self.game_object.type_name}")


class SceneScreenContainer(Screen[None]):
    pass


class ListOfObjects(ListView):
    BORDER_TITLE = "List of objects"


class EditorScreenContainer(SceneScreenContainer):
    BINDINGS = [
        Binding("escape", "escape", "Pause Menu"),
        Binding("ctrl+a", "select_all", "Select All"),
        Binding("ctrl+v", "copy_object", "Copy Object"),
        Binding("ctrl+s", "save_game", "Save Game"),
        Binding("ctrl+r", "try_map", "Try Map"),
        Binding("d", "delete_object", "Delete Object"),
    ]

    selected_objects: reactive[list[BaseObject | Player]] = reactive([], recompose=True)

    def __init__(self, map_chain: MapChain) -> None:
        self.map_chain = map_chain
        self.game: Optional[Editor] = None
        super().__init__()
        get_textlog().write(self.focused)
        self.game_display = Display(classes="editor")
        self.save_button = Button("Save", id="map_save", variant="success")
        self.download_button = Button(
            "Download map", id="map_download", variant="primary"
        )

        self.input_hp = Input(type="number", id="hp")

        self.objects: list[BaseObject] = [
            obj(layer_name="bg")
            for obj in sorted(CLASS_REGISTRY.values(), key=lambda x: x.type_name)
            if obj is not Player
        ]
        self.tool = None
        self.timers = [
            self.set_interval(
                1 / 30, self.animate_list_objects, name="animate_list_objects"
            ),
        ]

    def compose(self) -> ComposeResult:
        with Horizontal(id="detached-wrapper"):
            with Vertical(classes="left"):
                yield self.save_button
                yield self.download_button

                yield LabeledInput("HP:", self.input_hp)

                list_items = [GameObjectListItem(obj) for obj in self.objects]
                self.list_view = ListOfObjects(*list_items, initial_index=None)
                self.list_view.index = None
                yield self.list_view

            with Vertical(classes="center"):
                yield self.game_display
                yield SceneStatic("pos: ", classes="mouse_pos")

            with Vertical(classes="right"):
                yield SceneStatic("Selected object:")
                if len(self.selected_objects) == 1:
                    yield from self.selected_objects[0].edit_compose()
                elif len(self.selected_objects) > 1:
                    yield from self.multi_object_selection()

    def multi_object_selection(self) -> ComposeResult:
        input_layer: LabeledInput = LabeledInput(
            "Layer number:", Input(value="", type="number", id="object_layer_number")
        )
        if any(isinstance(x, Player) for x in self.selected_objects):
            yield input_layer
        else:
            delete_button = Button("Delete Object", id="delete_object", variant="error")
            copy_button = Button("Copy Object", id="copy_object", variant="warning")
            yield delete_button
            yield copy_button
            yield input_layer

    def animate_list_objects(self):
        for obj in self.objects:
            obj.reload()

    async def mouse_object_focus(self, event: MouseEvent, object: BaseObject | Player):
        if self.selected_objects or event.ctrl:
            return
        self.selected_objects = [object]
        await self.mark_as_selected([object], True)
        await self.recompose()

    async def mouse_switch_object_focus(
        self, event: MouseEvent, object: BaseObject | Player
    ):
        if event.ctrl:
            if object in self.selected_objects and len(self.selected_objects) > 1:
                self.selected_objects.remove(object)
                await self.mark_as_selected([object], False)
            elif object not in self.selected_objects:
                self.selected_objects.append(object)
                await self.mark_as_selected([object], True)

        else:
            await self.mark_as_selected(self.selected_objects, False)
            self.selected_objects = [object]
            await self.mark_as_selected([object], True)
        await self.recompose()

    async def mark_as_selected(
        self, objects: list[BaseObject | Player], selected: bool = True
    ) -> None:
        for object in objects:
            object.focused_editable(selected)

    async def focus_objects(self, objects: list[BaseObject | Player]):
        self.selected_objects = objects
        await self.mark_as_selected(self.selected_objects, True)
        await self.recompose()

    async def unfocus_all_objects(self):
        await self.mark_as_selected(self.selected_objects, False)
        self.selected_objects = []
        await self.recompose()

    async def unfocus_object(self, object: BaseObject | Player):
        self.selected_objects.remove(object)
        await self.mark_as_selected([object], False)
        await self.recompose()

    def save_game(self, file: pathlib.Path):
        if self.game is None:
            return
        d = {}
        d["objects"] = [asdict(x.to_parameters()) for x in self.game.objects]
        d["hp"] = int(self.input_hp.value)

        d["authors"] = self.game.authors
        d["game_version"] = GAME_VERSION
        d["name"] = self.game.map_name

        with open(file, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

        self.notify(f"Map: {file} saved!")

    def download_map(self):
        if self.game is None:
            return
        source = pathlib.Path(self.game.game_file)
        self.save_game(pathlib.Path.cwd() / source.name)

    async def delete_object(self):
        if self.game is None:
            return

        for object in list(
            [x for x in self.selected_objects if isinstance(x, BaseObject)]
        ):
            self.game.remove_object_from_dicts(object)
            self.delete_drawable(object)
            await self.unfocus_object(object)
        await self.recompose()

    async def action_copy_object(self):
        await self.copy_selected_objects()

    async def action_select_all(self):
        self.selected_objects = [obj for obj in self.game.objects]
        await self.mark_as_selected(self.selected_objects, True)
        await self.recompose()

    def action_save_game(self):
        if self.game is None:
            return
        self.save_game(self.game.game_file)

    def action_try_map(self):
        if self.game is None:
            return
        self.save_game(self.game.game_file)
        self.app.push_screen(GameScreenContainer(self.map_chain, test_only=True))

    async def action_delete_object(self):
        await self.delete_object()

    async def add_new_object(self, event: MouseEvent, object: BaseObject | None = None):
        if self.game is None:
            return

        await self.unfocus_all_objects()
        if not self.tool:
            return
        correction = Offset(-1, -1)
        if object is not None:
            correction = object.offset

        new_object = CLASS_REGISTRY[self.tool]
        new_object_instance = new_object(
            Offset(event.x, event.y) + correction, editable=True
        )
        self.mount_drawable(new_object_instance)
        self.game.add_object_to_dicts(new_object_instance)
        if event.ctrl:
            return
        self.tool = None
        self.list_view.index = None

    @on(Input.Changed, "#object_layer_number")
    def on_object_layer_number(self, event: Input.Changed):
        if not event.value.isnumeric():
            return
        for object in self.selected_objects:
            object.layer_number = int(event.value)

    @on(Input.Changed, "#object_width")
    def on_object_width(self, event: Input.Changed):
        if not event.value.isnumeric():
            return

        for object in self.selected_objects:
            object.set_size(
                Size(width=int(event.value), height=object.m_size.height),
                False,
            )

    @on(Input.Changed, "#object_height")
    def on_object_height(self, event: Input.Changed):
        if not event.value.isnumeric():
            return
        for object in self.selected_objects:
            object.set_size(
                Size(width=object.m_size.width, height=int(event.value)),
                False,
            )

    @on(Input.Changed, "#object_text")
    def on_object_text(self, event: Input.Changed):
        for object in self.selected_objects:
            if not hasattr(object, "text_value"):
                continue
            object.text_value = event.value

    @on(Button.Pressed, "#map_save")
    def on_map_save(self, event: Button.Pressed):
        if self.game is None:
            return
        self.save_game(self.game.game_file)

    @on(Button.Pressed, "#map_download")
    def on_map_download(self, event: Button.Pressed):
        self.download_map()

    @on(Button.Pressed, "#copy_object")
    async def on_copy_object(self, event: Button.Pressed):
        await self.copy_selected_objects()

    async def copy_selected_objects(self):
        if self.game is None:
            return
        if any(isinstance(object, Player) for object in self.selected_objects):
            return

        objects: list[BaseObject] = []
        offset = 2
        screen_size = self.game_display.screen_size
        for object in self.selected_objects:
            if (object.pos.y + offset) >= screen_size.height or (
                object.pos.x + offset
            ) >= screen_size.width:
                offset = -2

        for object in self.selected_objects:
            new_object_instance = object.copy(
                pos=Offset(object.pos.x + offset, object.pos.y + offset)
            )
            self.mount_drawable(new_object_instance)
            self.game.add_object_to_dicts(new_object_instance)
            objects.append(new_object_instance)
        await self.unfocus_all_objects()

        await self.focus_objects(objects)

    @on(Button.Pressed, "#delete_object")
    async def on_delete_object(self, event: Button.Pressed):
        await self.delete_object()

    @on(ScreenResume)
    async def resume_game(self):
        get_textlog().write("Resume game")
        if self.game is None:
            await self.create_game()
        assert self.game is not None
        get_textlog().write(self.BINDINGS)
        self.game.resume_game()

    @on(ScreenSuspend)
    def pause_game(self):
        get_textlog().write("Pause game")
        if self.game is not None:
            self.game.pause_game()

    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected):
        if self.game:
            self.tool = self.objects[event.index].type_name

    @on(MouseMove)
    async def on_mouse_move(self, event: MouseMove):
        if event.button == 0:
            return
        # TODO: Check if inside display

        for object in self.selected_objects:
            if event.ctrl:
                object.resize(event.delta, True)
            else:
                object.move(event.delta)

    @on(DisplayClicked)
    async def on_display_clicked(self, message: DisplayClicked):
        if self.game is None:
            return
        await self.add_new_object(message.event)

    @on(DisplayMouseHover)
    async def on_display_mouse_hover(self, message: DisplayMouseHover):
        if self.game is None:
            return
        self.query_one(".mouse_pos", Static).update(
            f"pos: y={message.event.y}, x={message.event.x}"
        )

    @on(PlayerClicked)
    async def on_player_clicked(self, message: PlayerClicked):
        await self.editable_clicked(message.event, message.object)

    @on(ObjectClicked)
    async def on_object_clicked(self, message: ObjectClicked):
        await self.editable_clicked(message.event, message.object)

    async def editable_clicked(self, event: Click, object: BaseObject | Player):
        if self.game is None:
            return

        if self.tool is not None:
            await self.add_new_object(event, object)
            return

        if (
            event.chain == 2
            and len(self.selected_objects) == 1
            and event.widget == self.selected_objects[0]
        ):
            await self.unfocus_object(self.selected_objects[0])
            return

        await self.mouse_switch_object_focus(event, object)

    @on(PlayerMouseDown)
    async def on_player_mouse_down(self, message: PlayerMouseDown):
        if self.game is None:
            return

        await self.mouse_object_focus(message.event, message.object)

    @on(ObjectMouseDown)
    async def on_object_mouse_down(self, message: ObjectMouseDown):
        if self.game is None:
            return

        await self.mouse_object_focus(message.event, message.object)

    @on(ObjectResized)
    async def on_object_resized(self, message: ObjectResized):
        if self.game is None:
            return
        if len(self.selected_objects) != 1:
            return

        try:
            self.query_one("#object_height", Input).value = str(message.new_size.height)
            self.query_one("#object_width", Input).value = str(message.new_size.width)
        except NoMatches:
            ...

    @on(LayerNumberChange)
    async def on_object_layer_number_change(self, message: LayerNumberChange):
        self.game_display.resort_layers()

    # ===== Handle key events =====

    async def action_escape(self):
        def check_if_restart(action: str) -> None:
            if action == "resume":
                return
            elif action == "to_menu":
                self.delete_game()
                self.dismiss()

        if self.tool is not None:
            self.tool = None
            self.list_view.index = None
        elif self.selected_objects:
            await self.unfocus_all_objects()
        else:
            self.app.push_screen(
                EditEndScreen(),
                check_if_restart,
            )

    async def create_game(self):
        get_textlog().write(f"Create game, {self.map_chain.current_map()}")
        self.game = Editor(
            self,
            get_textlog(),
            game_file=self.map_chain.current_map(),
        )
        # self.game.objects.update(set(self.objects))

    def delete_game(self):
        # TODO: Not used I think
        get_textlog().write("Delete game")
        if self.game is not None:
            self.game.end_game()
        self.game = None
        self.game_display.clear_all()

    async def end_game(self, win: bool = True):
        # TODO: Not used I think
        assert False

    async def on_end_game_dismiss(self, action: str):
        # TODO: Not used I think
        assert False
        if action == "to_menu":
            self.app.switch_screen("menu")
        elif action == "restart":
            await self.create_game()

    def mount_drawable(self, drawable: GameObjectStatic) -> None:
        self.game_display.mount_drawable(drawable)

    def delete_drawable(self, drawable: GameObjectStatic) -> None:
        self.game_display.delete_drawable(drawable)

    def stats_clear(self, config: MapConfigValues):
        self.input_hp.value = str(config.hp)


class CheckInputSystemScreen(MenuScreenBase[bool]):
    def __init__(self, input_manager: InputManager) -> None:
        self.input_manager = input_manager
        super().__init__()

    def compose(self) -> ComposeResult:
        # TODO: Fix CSS and reword
        yield Grid(
            Label(
                ("Press any movement key to start!\n"),
                id="question",
            ),
            id="dialog",
        )

    def action_go_back(self):
        self.dismiss(False)

    def on_key(self, event: events.Key):
        key_list = [
            "a",
            "w",
            "d",
            "h",
            "k",
            "l",
            "left_arrow",
            "up_arrow",
            "right_arrow",
            "left",
            "up",
            "right",
            "space",
        ]
        if event.key in key_list:
            if self.input_manager.is_pressed(key_list):
                self.dismiss(True)
            else:
                self.query_one("#question", Label).update(
                    (
                        "Pynput does not work!\n"
                        "Check troubleshooting to resolve this problem."
                        "Most likely you need to run terminal with sudo.\n"
                        "Press <Esc> to come back."
                    )
                )


class GameScreenContainer(SceneScreenContainer):
    BINDINGS = [
        Binding("escape", "pause_game", "Pause Menu"),
        Binding("r", "restart_game", "Restart Game"),
        Binding("z", "step", "Single step"),
        Binding("x", "start", "Single step"),
        Binding("c", "stop", "Single step"),
    ]

    def __init__(self, map_chain: MapChain, test_only: bool = False) -> None:
        self.map_chain = map_chain
        self.game: Optional[Game] = None
        super().__init__()
        get_textlog().write(self.focused)
        self.game_display = Display()
        self.points = Points()
        self.timer = TimeDisplay()
        self.hp_points = LifePoints()
        self.footer = FooterCustom()

        self.input_manager: InputManager = create_input_manager()
        self.should_check_input_system = should_check_input_system
        self.checking_input = False
        self.is_reseting = False
        self.test_only = test_only

    # ===== Compose =====

    def minimal_compose(self):
        with Horizontal(id="detached-wrapper"):
            with Vertical(classes="left"):
                yield self.timer
            with Vertical(classes="center"):
                yield self.game_display

            with Vertical(classes="right"):
                yield self.points
                yield self.hp_points
                # yield self.fps
        if DEBUG["footer"]:
            yield self.footer

    def compose(self) -> ComposeResult:
        yield from self.minimal_compose()

    # =====  =====

    def on_mount(self):
        self.input_manager.start()

    def on_unmount(self):
        self.input_manager.stop()

    def update(self):
        self.timer.update_time()

    # ===== Handle screens =====

    @on(ScreenResume)
    @work
    async def resume_game(self):
        global should_check_input_system
        get_textlog().write("Resume game")
        if self.game is None:
            if self.should_check_input_system and self.checking_input is False:
                self.checking_input = True
                await self.action_stop(True)
                input_system_works = await self.app.push_screen_wait(
                    CheckInputSystemScreen(self.input_manager)
                )
                if not input_system_works:
                    self.dismiss()
                    return
                await self.action_start(True)
                self.should_check_input_system = False
                should_check_input_system = False
                self.checking_input = False

            await self.create_game()
        else:
            self.timer.resume()
            self.game.resume_game()

    @on(ScreenSuspend)
    def pause_game(self):
        get_textlog().write("Pause game")
        self.timer.stop()
        if self.game is not None:
            self.game.pause_game()

    # ===== Handle key events =====
    # TODO: Little broken
    async def action_start(self, force: bool = False):
        if self.game and (DEBUG["step"] or force):
            self.game.resume_game()
            self.timer.resume()

    # TODO: Little broken
    async def action_stop(self, force: bool = False):
        if self.game and (DEBUG["step"] or force):
            self.game.pause_game()
            self.timer.stop()

    # TODO: Little broken
    async def action_step(self):
        if self.game and DEBUG["step"]:
            self.game.single_step()
            self.timer.add_one_step()

    def action_pause_game(self):
        async def check_if_restart(action: str) -> None:
            if action == "restart":
                await self.delete_game()
                self.dismiss(self.map_chain)
            elif action == "resume":
                return
            elif action == "discard":
                await self.delete_game()
                self.dismiss(None)

        if self.test_only:
            self.dismiss(self.map_chain)
            return

        self.app.push_screen("pause_menu", check_if_restart)

    async def action_restart_game(self):
        self.dismiss(self.map_chain)

    # ===== Game Live =====

    def is_finished(self):
        return self.points.is_finished()

    async def create_game(self):
        get_textlog().write(f"Create game, {self.map_chain.current_map()}")
        if self.game:
            return
        self.timer.stop()
        self.timer.reset()
        self.game = Game(
            self,
            get_textlog(),
            game_file=self.map_chain.current_map(),
        )

        self.timer.start()

    async def delete_game(self):
        get_textlog().write("Delete game")
        if self.game is not None:
            self.game.end_game()
        del self.game
        self.game = None
        self.game_display.clear_all()

    async def end_game(self, win: bool = True):
        get_textlog().write("End game")
        await self.delete_game()
        self.timer.stop()

        if self.test_only:
            self.dismiss(self.map_chain)
            return

        self.app.push_screen(
            EndScreen(
                self.points.val,
                self.points.max_val,
                self.timer.value,
                self.map_chain,
                win,
            ),
            self.on_end_game_dismiss,
        )

    async def reset_game(self):
        get_textlog().write("Reset game")
        if self.is_reseting:
            return
        self.is_reseting = True
        await self.delete_game()
        await self.create_game()
        self.is_reseting = False

    async def on_end_game_dismiss(self, action: str):
        if action == "to_menu":
            self.app.switch_screen("menu")
        elif action == "restart":
            self.dismiss(self.map_chain)
        elif action == "next_level":
            self.map_chain.next_map()
            await self.create_game()

    def stats_clear(self, config: MapConfigValues):
        self.points.clear()
        self.points.set_max(config.points)
        self.hp_points.set_max(config.hp)
        self.end_ball_to_win = config.winning_ball

    def mount_drawable(self, drawable: GameObjectStatic) -> None:
        self.game_display.mount_drawable(drawable)

    def delete_drawable(self, drawable: GameObjectStatic) -> None:
        self.game_display.delete_drawable(drawable)

    # ===== Handle Game Events =====

    @on(PointCollected)
    async def on_modify_points(self, event: PointCollected):
        self.points.add(event.val)
        if self.is_finished() and not self.end_ball_to_win:
            await self.end_game(True)

    @on(EndBallCollected)
    async def on_end_ball_collected(self, event: EndBallCollected):
        pass

    @on(HpChange)
    def on_modify_hp(self, event: HpChange):
        self.hp_points.add(event.val)

    @on(EndGame)
    async def on_end_game(self, event: EndGame):
        if event.won:
            await self.end_game(True)
        if self.hp_points.val <= 0:
            await self.end_game(False)
