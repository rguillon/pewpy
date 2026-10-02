"""The refinery: tank farms, process plants, flaring stacks, pipe racks and cooling towers between roads."""

import random

from pewpy.scenery.ground.settlement import Canvas, Layout, Rect, Settlement, Surface, grid, lots, shrink
from pewpy.scenery.params import Knobs


class Refinery(Settlement):
    knobs = ("block", "road", "lot", "units")

    def layout(self, rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
        """Units between roads (`block` apart, `road` wide), on lots `lot` wide at least: tank farms, process plants with
        furnaces, tall flaring stacks, pipe racks, cooling towers (`units`: one is picked per lot).
        """
        canvas = Canvas(rng, width, loop, Surface.STREET, (0.0, 0.0))
        road = knobs["road"]
        units = tuple(knobs["units"])
        for top, bottom, left, right in grid(width, loop, knobs["block"]):
            block = (top + road, bottom, left + road, right)
            for lot in lots(rng, block, knobs["lot"]):
                canvas.fill(shrink(lot, 0.008), Surface.YARD, rng.randrange(256))
                _refinery_unit(canvas, shrink(lot, 0.02), rng.choice(units))
        return canvas.layout()


def _refinery_unit(canvas: Canvas, lot: Rect, unit: str) -> None:
    rng = canvas.rng
    top, bottom, left, right = lot
    if unit == "tanks":
        count = 1 if rng.random() < 0.4 else 2  # one big tank or 2 x 2 smaller ones
        cell_height, cell_width = (bottom - top) / count, (right - left) / count
        height = rng.uniform(0.06, 0.16)
        for row in range(count):
            for column in range(count):
                cell = (top + row * cell_height, top + (row + 1) * cell_height)
                cell_x = (left + column * cell_width, left + (column + 1) * cell_width)
                size = min(cell_height, cell_width) * 0.85
                y, x = sum(cell) / 2, sum(cell_x) / 2
                canvas.add("tank", (y - size / 2, y + size / 2, x - size / 2, x + size / 2), height)
    elif unit == "plant":
        canvas.add("plant", shrink(lot, 0.01), rng.uniform(0.07, 0.16))
    elif unit == "cooling":  # one big cooling tower, or two smaller ones
        size = min(bottom - top, right - left)
        if (right - left) > 1.8 * (bottom - top):
            for middle in (left + (right - left) * 0.27, left + (right - left) * 0.73):
                half = min(size, (right - left) / 2) * 0.45
                y = (top + bottom) / 2
                canvas.add("cooling_tower", (y - half, y + half, middle - half, middle + half), rng.uniform(0.14, 0.2))
        else:
            y, x, half = (top + bottom) / 2, (left + right) / 2, size * 0.45
            canvas.add("cooling_tower", (y - half, y + half, x - half, x + half), rng.uniform(0.18, 0.28))
    elif unit == "stack":
        y, x = (top + bottom) / 2, (left + right) / 2
        size = rng.uniform(0.035, 0.05)
        canvas.add("stack", (y - size / 2, y + size / 2, x - size / 2, x + size / 2), rng.uniform(0.3, 0.45))
        canvas.add("plant", (top, top + (bottom - top) * 0.35, left, right), rng.uniform(0.05, 0.09))
    elif bottom - top > right - left:
        middle = (left + right) / 2
        canvas.add("pipes", (top, bottom, middle - 0.03, middle + 0.03), 0.03)
    else:
        middle = (top + bottom) / 2
        canvas.add("pipes", (middle - 0.03, middle + 0.03, left, right), 0.03)
