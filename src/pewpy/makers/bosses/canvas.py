"""A plan: a drawing seen from above, one character per cell, drawn with shapes."""

import math

from pewpy.makers.common.geometry import Point, inside


class Canvas:
    """A drawing being made: rows of characters, "." for nothing. Row 0 is the back (top of the screen)."""

    def __init__(self, width: int, height: int) -> None:
        self.w, self.h = width, height
        self.cells = [["."] * width for _ in range(height)]

    def set(self, x: int, y: int, char: str) -> None:
        """Set a cell (nothing happens outside the canvas)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            self.cells[y][x] = char

    def get(self, x: int, y: int) -> str:
        """Return a cell's character ("." outside the canvas)."""
        return self.cells[y][x] if 0 <= x < self.w and 0 <= y < self.h else "."

    def filled(self, x: int, y: int) -> bool:
        """Tell whether a cell has something drawn on it."""
        return self.get(x, y) != "."

    def mirror(self, x: float) -> float:
        """Return the column mirroring `x` across the canvas's middle."""
        return self.w - 1 - x

    def polygon(self, points: list[Point], char: str, side: str = "one") -> None:
        """Fill a polygon (the cells whose middle is inside); side "both" also fills its mirror image."""
        shapes = [points] + ([[(self.mirror(x), y) for x, y in points]] if side == "both" else [])
        for shape in shapes:
            xs, ys = [x for x, _ in shape], [y for _, y in shape]
            for y in self._span(min(ys), max(ys), self.h):  # only the cells in its bounding box
                for x in self._span(min(xs), max(xs), self.w):
                    if inside(x, y, shape):
                        self.set(x, y, char)

    @staticmethod
    def _span(low: float, high: float, size: int) -> range:
        return range(max(0, math.floor(low)), min(size, math.ceil(high) + 1))

    def rect(self, x0: float, x1: float, y0: float, y1: float, char: str, side: str = "one") -> None:
        """Fill a rectangle of cells, corners included; side "both" also fills its mirror image."""
        corners = [(x0 - 0.5, y0 - 0.5), (x1 + 0.5, y0 - 0.5), (x1 + 0.5, y1 + 0.5), (x0 - 0.5, y1 + 0.5)]
        self.polygon(corners, char, side)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, char: str) -> None:
        """Fill an ellipse (the cells whose middle is inside)."""
        for y in self._span(cy - ry, cy + ry, self.h):
            for x in self._span(cx - rx, cx + rx, self.w):
                if ((x - cx) / max(rx, 0.1)) ** 2 + ((y - cy) / max(ry, 0.1)) ** 2 <= 1.0:
                    self.set(x, y, char)

    def line(self, x0: float, y0: float, x1: float, y1: float, char: str, side: str = "one") -> None:
        """Draw a line of cells; side "both" also draws its mirror image."""
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(steps + 1):
            t = i / steps
            x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
            self.set(x, y, char)
            if side == "both":
                self.set(round(self.mirror(x)), y, char)

    def rows_chars(self) -> str:
        """Every character drawn."""
        return "".join({char for row in self.cells for char in row} - {"."})

    def cells_of(self, chars: str) -> list[tuple[int, int]]:
        """Return the cells holding any of `chars`."""
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.get(x, y) in chars]

    def rows(self) -> list[str]:
        """Return the drawing's rows, as strings."""
        return ["".join(row) for row in self.cells]
