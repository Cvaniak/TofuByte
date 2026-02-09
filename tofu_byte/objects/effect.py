class Effect:
    def __init__(self, pos) -> None:
        self.pos = pos
        self.life = 80

    def segment_color(self, y, x, color):
        from rich.segment import Segment
        from rich.style import Style

        down, up = "black", color
        if not y % 2:
            down, up = up, down

        return Segment(" ", Style(color=down, bgcolor=up))

    def segment_foo(self, y, x, color):
        from rich.segment import Segment
        from rich.style import Style
        from rich.color import Color, blend_rgb

        c = color.style.color
        c = c.get_truecolor()
        c = blend_rgb(
            c, Color.from_rgb(0, 200, 200).get_truecolor(), (self.life - x * 4) / 180
        )
        c = Color.from_triplet(c)

        # color.style.color = Color("red")

        down, up = "black", c
        if y % 2:
            down, up = up, down

        try:
            return Segment(color.text, Style(color=up, bgcolor=down))
        except Exception as e:
            print(e)
            return color

    def clean(self, mat):
        self.life -= 1
        w, h = len(mat[0]), len(mat)
        y, x = self.pos
        for i in range(-4, 4):
            for j in range(-4, 4):
                yy, xx = y + i, x + j
                if 0 <= xx < w and 0 <= yy < h:
                    if yy % 2:
                        mat[yy][xx] = self.segment_color(yy, xx, "black")
                    else:
                        mat[yy + 1][xx] = self.segment_color(yy, xx, "black")

    def draw(self, mat):
        w, h = len(mat[0]), len(mat)
        y, x = self.pos
        for i in range(-4, 4):
            for j in range(-4, 4):
                yy, xx = y + i, x + j
                if 0 <= xx < w and 0 <= yy < h:
                    if yy % 2:
                        color = mat[yy][xx]
                        mat[yy][xx] = self.segment_foo(yy, abs(i) + abs(j), color)
                    else:
                        color = mat[yy + 1][xx]
                        mat[yy + 1][xx] = self.segment_foo(yy, abs(i) + abs(j), color)
