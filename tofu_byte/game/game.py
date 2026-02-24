from __future__ import annotations
import asyncio
from collections import defaultdict, deque
from pathlib import Path
from time import perf_counter, time
from typing import TYPE_CHECKING, Any, Optional

from textual.message_pump import MessagePump
from textual._time import sleep as textual_sleep
from textual.geometry import Offset
from tofu_byte.config import DEBUG
from tofu_byte.objects.base_object import (
    BaseObject,
)
from tofu_byte.objects.game_object import GameObject
from tofu_byte.game.input_consumer import InputConsumer

from tofu_byte.objects.map import load_map
from tofu_byte.game.collision_manager import CollisionManager
from tofu_byte.player.player import Player
from tofu_byte.type_register import CLASS_REGISTRY
import tofu_byte.player.player_state as ps

from tofu_byte.tools.tools import Direction


if TYPE_CHECKING:
    from tofu_byte.screens.game_display import GameScreenContainer

TARGET_FPS = 30
FRAME_BUDGET_US = 1_000_000 // TARGET_FPS


class Scene(MessagePump):
    object_editable: bool = False

    def __init__(
        self,
        mediator: GameScreenContainer,
        *args: Any,
        game_file: Path,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.mediator = mediator
        self.game_file: Path = game_file

        self.timers = []
        self.objects: set[GameObject] = set()
        self.collision_manager = CollisionManager()

        self.load_map(self.game_file)
        self.player: Player
        assert self.player

    def clear_map(self):
        self.timers = []
        self.objects: set[GameObject] = set()
        self.collision_manager = CollisionManager()

    def load_map(self, game_file: Path) -> None:
        map_config = load_map(game_file)
        self._add_loaded_objects(map_config.objects.objects)

        self.mediator.stats_clear(map_config.config)
        self.map_name = map_config.metadata.name
        self.authors = map_config.metadata.authors
        self.map_game_version = map_config.metadata.game_version

    def remove_object_from_dicts(self, obj: GameObject):
        self.objects.discard(obj)

    def add_object_to_dicts(self, obj: GameObject):
        self.objects.add(obj)

    def _add_loaded_objects(self, objects: list[GameObject]) -> None:
        for obj in objects:
            self.mediator.mount_drawable(obj)
            self.objects.add(obj)
            obj.game_world_manager = self
            if isinstance(obj, Player):
                self.player: Player = obj
                if self.object_editable:
                    self.player.edit_state()
                obj.editable = True
            elif isinstance(obj, BaseObject):
                if self.object_editable:
                    obj.editable = True

    def _tick_all_objects(self) -> None:
        for obj in list(self.objects):
            obj.anim_state.tick()

    def update_clear_values(self) -> None:
        for obj in list(self.objects):
            obj.update_clear_values()

    def update_logic(self) -> None:
        for obj in list(self.objects):
            obj.update_logic()

    def update_visuals(self) -> None:
        for obj in list(self.objects):
            obj.update_visuals()

    async def update(self) -> None: ...

    # TODO: can be now removed as we moved from timers to while loop
    def pause_game(self):
        for timer in self.timers:
            timer.pause()

    # TODO: can be now removed as we moved from timers to while loop
    def resume_game(self) -> None:
        for timer in self.timers:
            timer.resume()

    # TODO: can be now removed as we moved from timers to while loop
    def end_game(self):
        for timer in self.timers:
            timer.stop()
        self.timers = []


class Editor(Scene):
    object_editable: bool = True

    def __init__(
        self, mediator: GameScreenContainer, *args: Any, game_file: Path, **kwargs: Any
    ) -> None:
        super().__init__(mediator, *args, game_file=game_file, **kwargs)
        self.timers = [
            self.set_interval(1 / 30, self.update, name="game_loop"),
        ]

    async def update(self) -> None:
        self._tick_all_objects()
        self.update_visuals()


class Game(Scene):
    def __init__(
        self,
        mediator: GameScreenContainer,
        *args: Any,
        game_file: Path,
        pause: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(mediator, *args, game_file=game_file, **kwargs)
        self.run = not pause
        self.is_reseting = False
        self.run_once = False
        self.set_interval_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        if DEBUG["fps"] or isinstance(self, ScenarioScene):
            self.step_times: dict[str, deque[int]] = defaultdict(
                lambda: deque(maxlen=120)
            )
            self.prev_time: int = round(time() * 1000)
            self.times: deque[int] = deque(maxlen=30)
            self.set_interval_task = asyncio.create_task(self.update_perf())
        else:
            self.set_interval_task = asyncio.create_task(self.update())

    async def handle_input(self):
        input_manager = self.mediator.input_manager
        input_set: set[Direction] = set()
        if input_manager.is_pressed(["a", "h", "left"]):
            input_set.add("l")
        if input_manager.is_pressed(["d", "l", "right"]):
            input_set.add("r")
        if input_manager.is_pressed(["k", "w", "space", "up"]):
            input_set.add("u")
        if input_manager.is_pressed(["j", "s", "down"]):
            input_set.add("d")

        for obj in self.objects:
            if isinstance(obj, InputConsumer):
                obj.handle_input(input_set)

    def remove_objects(self):
        to_remove: set[GameObject] = set()
        for obj in self.objects:
            if obj.should_remove:
                to_remove.add(obj)

        for i in to_remove:
            self.objects.remove(i)
            if isinstance(i, BaseObject):
                self.mediator.delete_drawable(i)

    def pause_game(self):
        self.run = False

    def resume_game(self) -> None:
        self.run = True

    def end_game(self): ...

    def process_collisions(self) -> None:
        self.collision_manager.prepare_frame(self.objects)
        for obj in self.objects:
            if obj.velocity != Offset(0, 0):
                self.collision_manager.move_and_collide(obj, obj.velocity)
            self.collision_manager.check_surroundings(obj)

    def single_step(self):
        if DEBUG["step"] or isinstance(self, ScenarioScene):
            self.run_once = True

    def _probe(self, name: str, start: float) -> float:
        now = perf_counter()
        self.step_times[name].append(int((now - start) * 1000000))
        return now

    async def step(self, t: float | None = None) -> float:
        self._tick_all_objects()
        if t is not None:
            t = self._probe("tick", t)

        self.update_clear_values()
        if t is not None:
            t = self._probe("clear", t)

        await self.handle_input()
        if t is not None:
            t = self._probe("input", t)

        self.process_collisions()
        if t is not None:
            t = self._probe("coll", t)

        self.update_logic()
        if t is not None:
            t = self._probe("logic", t)

        self.update_visuals()
        if t is not None:
            t = self._probe("visuals", t)

        self.remove_objects()
        if t is not None:
            t = self._probe("remove", t)

        self.mediator.update()
        if t is not None:
            t = self._probe("med", t)

        return t if t is not None else perf_counter()

    async def update(self) -> None:
        target_frame_time = 1 / TARGET_FPS
        next_frame_time = perf_counter()

        while True:
            if not self.run and not self.run_once:
                await textual_sleep(0.1)
                continue
            now = perf_counter()
            sleep_time = next_frame_time - now
            if sleep_time > 0:
                await textual_sleep(sleep_time)

            await self.step()

            self.run_once = False
            next_frame_time += target_frame_time

    async def update_perf(self) -> None:
        target_frame_time = 1 / TARGET_FPS
        next_frame_time = perf_counter()

        while True:
            if not self.run and not self.run_once:
                await textual_sleep(0.1)
                continue
            now = perf_counter()
            sleep_time = next_frame_time - now
            if sleep_time > 0:
                await textual_sleep(sleep_time)

            frame_start = perf_counter()
            await self.step(frame_start)

            if DEBUG["fps"] and self.step_times:
                avg_us = {k: sum(v) // len(v) for k, v in self.step_times.items()}

                frame_time_us = int((perf_counter() - frame_start) * 1_000_000)
                remaining_us = FRAME_BUDGET_US - frame_time_us

                _time: int = perf_counter() * 1_000_000
                self.times.append(_time - self.prev_time)
                self.prev_time = _time
                mid = sum(self.times) // len(self.times)

                if hasattr(self.mediator, "footer") and self.mediator.footer:
                    self.mediator.footer.fps.update(
                        " | ".join(f"{k}:{v:<5}µs" for k, v in avg_us.items())
                        + f" || frame:{frame_time_us:<5}µs"
                        + f" || headroom:{remaining_us:<5}µs"
                        + f" || fps:{1_000_000 / mid:.3f}"
                    )

            self.run_once = False
            next_frame_time += target_frame_time


class ScenarioScene(Game):
    def __init__(
        self,
        mediator: GameScreenContainer,
        *args: Any,
        scenario: Any,
        **kwargs: Any,
    ) -> None:
        self.scenario = scenario
        # Dummy Path since we load objects manually
        super().__init__(mediator, *args, game_file=Path("scenario.json"), **kwargs)
        self.step_index = 0
        self.is_finished = False
        self.run = False

    def load_map(self, game_file: Path) -> None:
        self.objects = set()

        for data in self.scenario.objects_data:
            obj_cls = CLASS_REGISTRY[data["type"]]
            obj = obj_cls.from_json(data)
            obj.type_name = data["type"]
            obj.game_world_manager = self
            self.add_object_to_dicts(obj)
            self.mediator.mount_drawable(obj)

        self.player = Player(start_pos=self.scenario.player_start)
        self.player.game_world_manager = self

        state_cls = getattr(ps, self.scenario.starting_state)
        self.player.change_state(state_cls(self.player))

        self.objects.add(self.player)
        self.mediator.mount_drawable(self.player)

    async def handle_input(self):
        if self.is_finished:
            return

        if self.step_index < len(self.scenario.timeline):
            input_set = self.scenario.timeline[self.step_index]
            self.player.handle_input(input_set)
            self.step_index += 1
        else:
            self.is_finished = True

    def next_step(self):
        self.single_step()
