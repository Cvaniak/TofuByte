from random import randint
from typing import NamedTuple, Dict
from rich.color import Color, blend_rgb
from rich.color_triplet import ColorTriplet


LIGHT_STEPS = 64
PRE_BR = Color.parse("black")


class bColor(NamedTuple):
    color: Color
    triplet: ColorTriplet
    c_blended: Dict[int, Color]

    @classmethod
    def full(cls, color: str) -> "bColor":
        c = Color.parse(color)
        t = c.get_truecolor()
        d = {
            x: Color.from_triplet(
                blend_rgb(t, PRE_BR.get_truecolor(), (LIGHT_STEPS - x) / LIGHT_STEPS)
            )
            for x in range(LIGHT_STEPS + 1)
        }
        return cls(color=c, triplet=t, c_blended=d)


BLUE = bColor.full("blue")
GREEN = bColor.full("green")
MAGENTA = bColor.full("magenta")
RED = bColor.full("red")
WHITE = bColor.full("white")
# WHITE = "white"
BLACK = bColor.full("rgb(0,0,0)")
# BLACK = "black"
DARK_BLUE = bColor.full("rgb(0,100,150)")
DARK_ORANGE = bColor.full("rgb(92,56,32)")
LIME = bColor.full("rgb(5, 235, 20)")
r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
RANDOM = bColor.full(f"rgb({r},{g},{b})")

BACKGROUND = "rgb(10,10,20)"

PLAYER = LIME

# GROUND_BOTTOM = WHITE
GROUND_BOTTOM = "rgb(50,50,65)"
# GROUND_TOP = DARK_BLUE
GROUND_TOP = "rgb(80,80,90)"
# SPIKES_BG = BACKGROUND
SPIKES_BG = "black"
# SPIKES_FG = DARK_ORANGE
# SPIKES_FG = RANDOM
# SPIKES_FG = f"rgb({r},{g},{b})"
SPIKES_FG = "rgb(255,200,0)"
# LIGHT_FG = bColor.full("rgb(250,204,0)")
LIGHT_FG = "rgb(250,204,0)"
# LIGHT_BG = bColor.full("rgb(230,140,0)")
LIGHT_BG = "rgb(230,140,0)"

# STAR_BG = BACKGROUND
STAR_BG = "black"
# STAR_FG = bColor.full("rgb(230,230,0)")
STAR_FG = "rgb(253,208,23)"
