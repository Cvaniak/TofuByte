from __future__ import annotations
import asyncio
from collections import defaultdict, deque
from pathlib import Path
from time import perf_counter, time

from textual.message_pump import MessagePump
from textual._time import sleep as textual_sleep
from tofu_byte.config import DEBUG
from tofu_byte.objects.base_object import BaseObject

from tofu_byte.objects.map import load_map
from tofu_byte.player.collision import Collision, CollisionEvent
from tofu_byte.player.player import Player

from typing import TYPE_CHECKING, Any

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
        self.objects: set[BaseObject | Player] = set()
        self.colliders: set[BaseObject] = set()
        self.collision_logic = Collision(self)

        self.load_map(self.game_file)
        self.player: Player
        assert self.player

    def clear_map(self):
        self.timers = []
        self.objects: set[BaseObject | Player] = set()
        self.colliders: set[BaseObject] = set()
        self.collision_logic = Collision(self)

    def load_map(self, game_file: Path) -> None:
        map_config = load_map(game_file)
        self._add_loaded_objects(map_config.objects.objects)

        self.mediator.stats_clear(map_config.config)
        self.map_name = map_config.metadata.name
        self.authors = map_config.metadata.authors
        self.map_game_version = map_config.metadata.game_version

    def remove_object_from_dicts(self, object: BaseObject):
        self.colliders.discard(object)
        self.objects.discard(object)

    def add_object_to_dicts(self, object: BaseObject):
        if object.triggers or object.blocks:
            self.colliders.add(object)
        self.objects.add(object)

    def _add_loaded_objects(self, objects: list[BaseObject | Player]) -> None:
        for obj in objects:
            self.mediator.mount_drawable(obj)
            self.objects.add(obj)
            if isinstance(obj, Player):
                self.player: Player = obj
                if self.object_editable:
                    self.player.edit_state()
            else:
                if self.object_editable:
                    obj.editable = True
                self.colliders.add(obj)

    def update_effects(self) -> None:
        for obj in self.objects:
            if not isinstance(obj, BaseObject):
                continue
            obj.reload()
        self.player.change_color()

    def check_collisions(self):
        collisions: set[CollisionEvent] = self.collision_logic.gather_collisions(
            self.player
        )

        blocked_axes: set[CollisionEvent] = set()

        for event in collisions:
            obj = event.obj

            if obj.blocks_movement(event):
                blocked_axes.add(event)

            if obj.triggers:
                obj.on_collision(event)

        for event in blocked_axes:
            self.player.on_collision(event)

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
        self.update_effects()
        self.player.show()


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
        if DEBUG["fps"]:
            self.step_times: dict[str, deque[int]] = defaultdict(
                lambda: deque(maxlen=120)
            )
            self.prev_time: int = round(time() * 1000)
            self.times: deque[int] = deque(maxlen=30)
            self.run_once = False
            self.set_interval_task = asyncio.create_task(self.update_perf())
        else:
            self.set_interval_task = asyncio.create_task(self.update())

    def update_clear_values(self):
        for obj in self.objects:
            obj.update_clear_values()

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

        self.player.handle_input(input_set)

    def remove_objects(self):
        to_remove: set[BaseObject | Player] = set()
        for obj in self.objects:
            if obj.should_remove:
                to_remove.add(obj)

        for i in to_remove:
            self.objects.remove(i)
            self.colliders.remove(i)
            self.mediator.delete_drawable(i)

    def pause_game(self):
        self.run = False

    def resume_game(self) -> None:
        self.run = True

    def end_game(self): ...

    def single_step(self):
        if DEBUG["step"]:
            self.run_once = True

    async def update(self) -> None:
        target_frame_time = 1 / TARGET_FPS
        next_frame_time = perf_counter()

        while True:
            if not self.run:
                await textual_sleep(0.1)
                continue
            now = perf_counter()
            sleep_time = next_frame_time - now
            if sleep_time > 0:
                await textual_sleep(sleep_time)

            self.update_clear_values()
            await self.handle_input()
            self.check_collisions()
            self.player.update_states()
            self.remove_objects()
            self.mediator.update()
            self.update_effects()
            self.player.show()

            next_frame_time += target_frame_time

    def _probe(self, name: str, start: float) -> float:
        now = perf_counter()
        self.step_times[name].append(int((now - start) * 1000000))
        return now

    async def update_perf(self) -> None:
        target_frame_time = 1 / TARGET_FPS
        next_frame_time = perf_counter()

        while True:
            if not self.run and not (DEBUG["step"] and self.run_once):
                await textual_sleep(0.1)
                continue
            now = perf_counter()
            sleep_time = next_frame_time - now
            if sleep_time > 0:
                await textual_sleep(sleep_time)

            frame_start = perf_counter()
            t = frame_start

            self.update_clear_values()
            t = self._probe("clear", t)

            await self.handle_input()
            t = self._probe("input", t)

            self.check_collisions()
            t = self._probe("coll", t)

            self.player.update_states()
            t = self._probe("states", t)

            self.update_effects()
            t = self._probe("effects", t)

            self.remove_objects()
            t = self._probe("remove", t)

            self.mediator.update()
            t = self._probe("med", t)

            self.player.show()
            t = self._probe("show", t)

            if DEBUG["fps"] and self.step_times:
                avg_us = {k: sum(v) // len(v) for k, v in self.step_times.items()}

                frame_time_us = int((perf_counter() - frame_start) * 1_000_000)
                remaining_us = FRAME_BUDGET_US - frame_time_us

                _time: int = perf_counter() * 1_000_000
                self.times.append(_time - self.prev_time)
                self.prev_time = _time
                mid = sum(self.times) // len(self.times)

                self.mediator.footer.fps.update(
                    " | ".join(f"{k}:{v:<5}µs" for k, v in avg_us.items())
                    + f" || frame:{frame_time_us:<5}µs"
                    + f" || headroom:{remaining_us:<5}µs"
                    + f" || fps:{1_000_000 / mid:.3f}"
                )

            self.run_once = False
            next_frame_time += target_frame_time
