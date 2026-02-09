import math
from time import monotonic
from typing import Any
from textual.color import Color
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Static, Digits
from rich.text import Text

from tofu_byte.screens.const import YOU_LOOSE, YOU_WON


def minmax(value: int, min_v: int = 0, max_v: int = 255):
    return min(max(value, min_v), max_v)


class MyText(Text):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MyText):
            return NotImplemented
        return (
            self.plain == other.plain
            and self._spans == other._spans
            and self.style == other.style
        )


class ScreenTitle(Static):
    def __init__(
        self,
        text: str,
        *args: Any,
        start_values: tuple[int, int, int] = (128, 128, 128),
        modify_values: tuple[int, int, int] = (127, 127, 127),
        density: float = 8.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.text = text
        self.density = density
        self.phase = 0.0
        self.start_values = start_values
        self.modify_values = modify_values
        wh = self.text.split("\n")
        self.h = len(wh)
        self.w = len(wh[0])

    def on_mount(self) -> None: ...

    def start_gradient(self):
        if hasattr(self, "timer"):
            return
        self.timer = self.set_interval(0.05, self.gradient_update, name="gradient")

    def stop_gradient(self):
        self.timer.pause()
        self.timer.stop()
        del self.timer
        self._timers.clear()

    def gradient_update(self) -> None:
        self.phase += 0.15
        self.refresh()

    def render(self) -> Text:
        result = Text()

        # visible = [c for c in self.text if c != "\n"]
        total = max((self.w + self.h) * self.density, 1)

        x = 0
        y = 0
        for ch in self.text:
            if ch == "\n":
                result.append("\n")
                y += 1
                x = 0
                continue
            i = x + y

            t = (i / total) * 2 * math.pi + self.phase
            rs, gs, bs = self.start_values
            rm, gm, bm = self.modify_values
            r = minmax(rs + rm * math.sin(t))
            g = minmax(gs + gm * math.sin(t + math.pi / 2))
            b = minmax(bs + bm * math.sin(t + math.pi))

            result.append(ch, style=f"rgb({int(r)},{int(g)},{int(b)})")
            x += 1

        return result


class ThemeScreenTitle(ScreenTitle):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        start_values, modify_values = self._start_values(self.app.theme)
        super().__init__(
            *args, start_values=start_values, modify_values=modify_values, **kwargs
        )
        self.watch(self.app, "theme", self.on_theme_change, init=False)

    def _from_values(self, theme: str) -> str:
        return (
            self.app.available_themes[theme].to_color_system().generate()["secondary"]
        )

    def _to_values(self, theme: str) -> str:
        return self.app.available_themes[theme].to_color_system().generate()["accent"]

    def on_theme_change(self, new_theme: str) -> None:
        self.start_values, self.modify_values = self._start_values(new_theme)

    def _start_values(
        self, theme: str
    ) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        prim = Color.parse(self._from_values(theme)).rgb
        sec = Color.parse(self._to_values(theme)).rgb
        avg: list[int] = []
        change: list[int] = []
        for a, b in zip(prim, sec):
            avg.append((a + b) // 2)
            change.append(abs(a - b) // 2)
        return tuple(avg), tuple(change)


class YouWonScreenTitle(ThemeScreenTitle):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(YOU_WON, *args, **kwargs)

    def _from_values(self, theme: str) -> str:
        return (
            self.app.available_themes[theme]
            .to_color_system()
            .generate()["success-darken-1"]
        )

    def _to_values(self, theme: str) -> str:
        return (
            self.app.available_themes[theme]
            .to_color_system()
            .generate()["success-lighten-1"]
        )


class YouLoseScreenTitle(ThemeScreenTitle):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(YOU_LOOSE, *args, **kwargs)

    def _from_values(self, theme: str) -> str:
        return (
            self.app.available_themes[theme]
            .to_color_system()
            .generate()["error-darken-1"]
        )

    def _to_values(self, theme: str) -> str:
        return (
            self.app.available_themes[theme]
            .to_color_system()
            .generate()["error-lighten-1"]
        )


class PrimaryScreenTitle(ThemeScreenTitle): ...


class GameObjectStatic(Static): ...


class MapName(GameObjectStatic):
    def set_map(self, map_name: str):
        self.update(map_name)


class GameDigits(Digits):
    DEFAULT_CSS = """
    Digits {
        width: 1fr;
        height: auto;
        text-align: center;
        text-style: bold;
        box-sizing: content-box;
    }
    """
    ...


class PointSystem:
    def __init__(self, init_val: int = 0, max_val: int = 0) -> None:
        self.val: int = init_val
        self.max_val: int = max_val

    def set_max(self, val: int):
        self.max_val = val
        self.update_display()

    def add(self, val: int):
        self.val += val
        self.update_display()

    def is_finished(self) -> bool:
        return self.max_val <= self.val

    def clear(self):
        self.val = 0
        self.max_val = 0
        self.update_display()

    def update_display(self): ...


class Points(GameDigits, PointSystem):
    def __init__(self, init_val: int = 0, max_val: int = 0) -> None:
        super(GameDigits, self).__init__()
        PointSystem.__init__(self, init_val, max_val)

    def on_mount(self):
        self.update_display()

    def add(self, val: int):
        self.val += val
        self.update_display()

    def update_display(self):
        self.update(f"{self.val}x{self.max_val}")


class Heart(Static): ...


class LifePoints(Container, PointSystem):
    """
    ◢◣◢◣
       ◢
      ▗▖▗▖     ▗▄ ▄▖       ▟   ▟█▄█▙  ▟█▄█▙
      ▜██▛     ▜███▛   ▘       ▝▜█▛▘  ▝▜██▘
       ▜▛       ▝▂▘  ▂▄▃  ▜▛▄    ▆      ▆
    """

    state_a = "▟█▄█▙\n▝▜█▛▘\n\n"
    state_b = "▗▄ ▄▖\n" + "▜███▛\n" + " ▝▀▘\n"
    heart_state = 1

    def __init__(self, init_val: int = 0, max_val: int = 0) -> None:
        super(Container, self).__init__()
        PointSystem.__init__(self, init_val, max_val)
        self.value_display = GameDigits("1")

    def set_max(self, val: int):
        self.val = val
        self.update_display()

    def update_display(self):
        self.value_display.update(str(self.val))

    def heart_update(self):
        if self.heart_state:
            self.heart.update(self.state_b)
        else:
            self.heart.update(self.state_a)
        self.heart_state = 1 - self.heart_state

    def compose(self):
        self.heart = Heart(self.state_a)
        self.set_interval(2, self.heart_update, name="heart_update")
        with Horizontal():
            yield self.heart
            yield self.value_display


class TimeDisplay(GameDigits):
    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = 0

    def reset(self):
        self.total = 0
        self.time = 0

        self.start_time = monotonic()
        # self.update_timer.resume()

    def setup(self) -> None:
        # self.update_timer = self.set_interval(1 / 15, self.update_time, pause=True)
        self.reset()

    def on_mount(self) -> None:
        self.setup()

    def update_time(self) -> None:
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        minutes, seconds = divmod(time, 60)
        _, minutes = divmod(minutes, 60)
        self.update(f"{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        self.reset()

    def stop(self):
        # self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def resume(self) -> None:
        self.start_time = monotonic()
        # self.update_timer.resume()

    def add_one_step(self):
        self.total += ((1 / 60) / 60) / 30
