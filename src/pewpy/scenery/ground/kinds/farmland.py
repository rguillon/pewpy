"""Farmland: patchwork fields, hedges, orchards, farms, greenhouses, trees along dirt roads."""

import random

from pewpy.scenery.ground.settlement import Canvas, Layout, Rect, Settlement, Surface, grid, lots, shrink
from pewpy.scenery.params import Knobs


class Farmland(Settlement):
    """Farmland: patchwork fields between dirt roads, farms and orchards."""

    knobs = (
        "block",
        "road",
        "lot",
        "farm_share",
        "orchard_share",
        "greenhouse_share",
        "hedge_share",
        "fields",
        "tree_size",
    )

    def layout(self, rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
        """Lay out patchwork fields (`fields`: one is picked per lot) between dirt roads (`block` apart, `road` wide).

        Some have hedges around (`hedge_share`); orchards (`orchard_share`), farms with a house, a barn and a silo
        (`farm_share`), rows of greenhouses (`greenhouse_share`), trees along the roads.
        """
        canvas = Canvas(rng, width, loop, Surface.DIRT_ROAD, knobs["tree_size"])
        road = knobs["road"]
        fields = tuple(Surface[name.upper()] for name in knobs["fields"])
        farms, orchards = knobs["farm_share"], knobs["farm_share"] + knobs["orchard_share"]
        greenhouses = orchards + knobs["greenhouse_share"]
        for top, bottom, left, right in grid(width, loop, knobs["block"]):
            block = (top + road, bottom, left + road, right)
            for lot in lots(rng, block, knobs["lot"]):
                roll = rng.random()
                if roll < farms:
                    _farm(canvas, lot)
                elif roll < orchards:
                    _orchard(canvas, lot)
                elif roll < greenhouses:
                    _greenhouses(canvas, lot)
                else:
                    canvas.fill(lot, rng.choice(fields), rng.randrange(256))
                    if rng.random() < knobs["hedge_share"]:
                        _hedges(canvas, lot)
            for _ in range(rng.randrange(3)):  # a few trees along the road
                x = rng.uniform(left + road, right)
                canvas.tree(x, top + road + 0.012)
        return canvas.layout()


def _farm(canvas: Canvas, lot: Rect) -> None:
    rng = canvas.rng
    canvas.fill(lot, Surface.PASTURE, rng.randrange(256))
    top, bottom, left, right = shrink(lot, 0.015)
    yard = (top, min(bottom, top + 0.12), left, min(right, left + 0.14))
    canvas.fill(yard, Surface.FARMYARD)
    y0, _, x0, _ = yard
    canvas.add("house", (y0 + 0.01, y0 + 0.045, x0 + 0.01, x0 + 0.06), 0.03)
    canvas.add("barn", (y0 + 0.06, y0 + 0.11, x0 + 0.01, x0 + 0.09), 0.04)
    canvas.add("silo", (y0 + 0.055, y0 + 0.08, x0 + 0.105, x0 + 0.13), rng.uniform(0.07, 0.1))
    for _ in range(3):
        canvas.tree(x0 + rng.uniform(0.07, 0.13), y0 + rng.uniform(0.0, 0.04))


def _greenhouses(canvas: Canvas, lot: Rect) -> None:
    """Long greenhouses side by side, on packed earth."""
    canvas.fill(lot, Surface.FARMYARD)
    top, bottom, left, right = shrink(lot, 0.012)
    along_x = (right - left) >= (bottom - top)
    across = (bottom - top) if along_x else (right - left)
    count = max(1, int(across / 0.035))
    width = across / count
    for index in range(count):
        a, b = index * width + 0.004, (index + 1) * width - 0.004
        rect = (top + a, top + b, left, right) if along_x else (top, bottom, left + a, left + b)
        canvas.add("greenhouse", rect, 0.018)


def _orchard(canvas: Canvas, lot: Rect) -> None:
    canvas.fill(lot, Surface.PASTURE, canvas.rng.randrange(256))
    top, bottom, left, right = shrink(lot, 0.02)
    spacing = 0.042
    for row in range(int((bottom - top) / spacing) + 1):
        for column in range(int((right - left) / spacing) + 1):
            canvas.tree(left + column * spacing, top + row * spacing, 0.026)


def _hedges(canvas: Canvas, lot: Rect) -> None:
    top, bottom, left, right = lot
    thick, height = 0.01, 0.014
    for rect in (
        (top, top + thick, left, right),
        (bottom - thick, bottom, left, right),
        (top + thick, bottom - thick, left, left + thick),
        (top + thick, bottom - thick, right - thick, right),
    ):
        canvas.add("hedge", rect, height)
