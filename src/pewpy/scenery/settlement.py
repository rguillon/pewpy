"""Built-up grounds on a smooth relief (relief.py): the city, the refinery and the farmland.

A layout is what the ground is covered with, as a surface map painted by the ground shader (streets, pavements,
yards, fields...), plus the props standing on it: buildings, tanks, stacks, pipe racks, houses, barns, silos, trees,
hedges. prop_meshes.py builds the props, ground_shader.py draws both.

Each settlement's numbers (block sizes, shares, building heights...) come from the level's scenery (`layout`, see
params.py and KNOBS below). Positions are in world units: x from the ground's left edge, y down the loop (like the relief's rows); the layout
loops along y like the rest of the ground (the grids of blocks divide the loop exactly and nothing crosses its end).
Independent from Panda3D.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import IntEnum
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

from pewpy.scenery.params import Knobs

SURFACE_STEP = 0.005  # world units between two points of the surface map


class Surface(IntEnum):
    """What the ground is covered with (the ground shader's colors for each, see ground_shader.py)."""

    NATURAL = 0  # the biome's own: park grass in the city, scrub by the refinery, grass on the farms
    STREET = 1
    PAVEMENT = 2  # sidewalks and plazas
    YARD = 3  # stained concrete around the refinery's units
    DIRT_ROAD = 4
    WHEAT = 5
    CROP = 6
    PLOWED = 7
    LAVENDER = 8
    PASTURE = 9
    FARMYARD = 10


@dataclass(frozen=True)
class Prop:
    """Something standing on the ground. `kind`: "building", "house", "barn", "silo", "tank", "plant", "stack",
    "pipes", "tree" or "hedge"; `seed` picks its colors and details (see prop_meshes.py)."""

    kind: str
    x: float  # middle of its footprint
    y: float
    width: float  # along x
    length: float  # along y
    height: float
    seed: int
    base: float = 0.0  # height of the ground under it, set once it's placed on the relief


@dataclass
class Layout:
    surface: NDArray[np.uint8]  # (rows, columns): a Surface every SURFACE_STEP
    variant: NDArray[np.uint8]  # (rows, columns): a number per lot or field (its shade, its rows' direction)
    props: list[Prop]
    width: float
    loop: float


Rect = tuple[float, float, float, float]  # (top, bottom, left, right): y from top to bottom, x from left to right
# (rng, width, loop length, knobs) -> the layout
SettlementGenerator = Callable[[random.Random, float, float, Knobs], Layout]


class _Canvas:
    """The surface map being painted, and the props placed so far."""

    def __init__(
        self, rng: random.Random, width: float, loop: float, background: Surface, tree_size: tuple[float, float]
    ) -> None:
        self.rng = rng
        self.tree_size = tree_size  # crown diameters
        self.width = width
        self.loop = loop
        rows, columns = round(loop / SURFACE_STEP), round(width / SURFACE_STEP)
        self.surface = np.full((rows, columns), background, dtype=np.uint8)
        self.variant = np.zeros((rows, columns), dtype=np.uint8)
        self.props: list[Prop] = []

    def fill(self, rect: Rect, surface: Surface, variant: int = 0) -> None:
        top, bottom, left, right = (round(edge / SURFACE_STEP) for edge in rect)
        self.surface[top:bottom, max(left, 0) : right] = surface
        self.variant[top:bottom, max(left, 0) : right] = variant

    def add(self, kind: str, rect: Rect, height: float) -> None:
        top, bottom, left, right = rect
        middle = ((left + right) / 2, (top + bottom) / 2)
        self.props.append(Prop(kind, *middle, right - left, bottom - top, height, self.rng.randrange(1 << 30)))

    def tree(self, x: float, y: float, size: float | None = None) -> None:
        size = size or self.rng.uniform(*self.tree_size)
        rect = (y - size / 2, y + size / 2, x - size / 2, x + size / 2)
        self.add("tree", rect, size * self.rng.uniform(0.8, 1.1))

    def layout(self) -> Layout:
        return Layout(self.surface, self.variant, self.props, self.width, self.loop)


def grid(width: float, loop: float, size: float) -> list[Rect]:
    """Blocks about `size` wide, the loop divided exactly (so the grid loops)."""
    rows = [loop * i / max(round(loop / size), 1) for i in range(max(round(loop / size), 1) + 1)]
    columns = [width * i / max(round(width / size), 1) for i in range(max(round(width / size), 1) + 1)]
    return [(top, bottom, left, right) for top, bottom in pairwise(rows) for left, right in pairwise(columns)]


def split(rng: random.Random, start: float, end: float, smallest: float) -> list[tuple[float, float]]:
    """Cut [start, end] into 1 to 3 pieces, none shorter than `smallest`."""
    pieces = rng.choice((1, 2, 2, 3))
    while pieces > 1 and (end - start) < smallest * pieces:
        pieces -= 1
    cuts = sorted(rng.uniform(start + smallest, end - smallest) for _ in range(pieces - 1))
    for index in range(1, len(cuts)):
        cuts[index] = max(cuts[index], cuts[index - 1] + smallest)
    edges = [start, *[cut for cut in cuts if cut < end - smallest / 2], end]
    return list(pairwise(edges))


def lots(rng: random.Random, rect: Rect, smallest: float) -> list[Rect]:
    top, bottom, left, right = rect
    return [(a, b, c, d) for a, b in split(rng, top, bottom, smallest) for c, d in split(rng, left, right, smallest)]


def shrink(rect: Rect, margin: float) -> Rect:
    top, bottom, left, right = rect
    return (top + margin, bottom - margin, left + margin, right - margin)


def city(rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
    """Blocks of buildings between streets (`block` apart, `street` wide): mostly low buildings, some mid-rises,
    a few towers (`tower_share`, `midrise_share`; their heights between `tower`, `midrise`, `lowrise`), the odd park
    (`park_share`). Lots are `lot` wide at least, a `sidewalk` around them."""
    canvas = _Canvas(rng, width, loop, Surface.STREET, knobs["tree_size"])
    street = knobs["street"]
    towers, midrises = knobs["tower_share"], knobs["tower_share"] + knobs["midrise_share"]
    for top, bottom, left, right in grid(width, loop, knobs["block"]):
        block = (top + street, bottom, left + street, right)  # the street runs along its top and left
        canvas.fill(block, Surface.PAVEMENT)
        for part in _alleys(canvas, block, knobs["alley"], knobs["alley_share"]):
            for lot in lots(rng, shrink(part, knobs["sidewalk"]), knobs["lot"]):
                if rng.random() < knobs["park_share"]:
                    _park(canvas, lot)
                    continue
                roll = rng.random()
                span = knobs["tower"] if roll < towers else knobs["midrise"] if roll < midrises else knobs["lowrise"]
                canvas.add("building", shrink(lot, rng.uniform(0.004, 0.012)), rng.uniform(*span))
    return canvas.layout()


def _alleys(canvas: _Canvas, block: Rect, width: float, share: float) -> list[Rect]:
    """Some blocks (`share` of them) are cut in two by a narrow alley, one way or the other: the two halves (or the
    whole block)."""
    rng = canvas.rng
    if rng.random() >= share:
        return [block]
    top, bottom, left, right = block
    if rng.random() < 0.5:  # across the block
        middle = rng.uniform(top + 0.35 * (bottom - top), top + 0.65 * (bottom - top))
        alley = (middle - width / 2, middle + width / 2, left, right)
        halves = [(top, alley[0], left, right), (alley[1], bottom, left, right)]
    else:  # along it
        middle = rng.uniform(left + 0.35 * (right - left), left + 0.65 * (right - left))
        alley = (top, bottom, middle - width / 2, middle + width / 2)
        halves = [(top, bottom, left, alley[2]), (top, bottom, alley[3], right)]
    canvas.fill(alley, Surface.STREET)
    return halves


def _park(canvas: _Canvas, lot: Rect) -> None:
    canvas.fill(lot, Surface.NATURAL)
    top, bottom, left, right = shrink(lot, 0.02)
    for _ in range(round((bottom - top) * (right - left) / 0.004)):
        canvas.tree(canvas.rng.uniform(left, right), canvas.rng.uniform(top, bottom))


def refinery(rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
    """Units between roads (`block` apart, `road` wide), on lots `lot` wide at least: tank farms, process plants with
    furnaces, tall flaring stacks, pipe racks (`units`: one is picked per lot)."""
    canvas = _Canvas(rng, width, loop, Surface.STREET, (0.0, 0.0))
    road = knobs["road"]
    units = tuple(knobs["units"])
    for top, bottom, left, right in grid(width, loop, knobs["block"]):
        block = (top + road, bottom, left + road, right)
        for lot in lots(rng, block, knobs["lot"]):
            canvas.fill(shrink(lot, 0.008), Surface.YARD, rng.randrange(256))
            _refinery_unit(canvas, shrink(lot, 0.02), rng.choice(units))
    return canvas.layout()


def _refinery_unit(canvas: _Canvas, lot: Rect, unit: str) -> None:
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
    elif unit == "stack":
        y, x = (top + bottom) / 2, (left + right) / 2
        size = rng.uniform(0.035, 0.05)
        canvas.add("stack", (y - size / 2, y + size / 2, x - size / 2, x + size / 2), rng.uniform(0.3, 0.45))
        canvas.add("plant", (top, top + (bottom - top) * 0.35, left, right), rng.uniform(0.05, 0.09))
    else:  # a pipe rack along the lot's longer side
        if bottom - top > right - left:
            middle = (left + right) / 2
            canvas.add("pipes", (top, bottom, middle - 0.03, middle + 0.03), 0.03)
        else:
            middle = (top + bottom) / 2
            canvas.add("pipes", (middle - 0.03, middle + 0.03, left, right), 0.03)


def farmland(rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
    """Patchwork fields (`fields`: one is picked per lot) between dirt roads (`block` apart, `road` wide), some with
    hedges around (`hedge_share`), orchards (`orchard_share`), farms with a house, a barn and a silo (`farm_share`),
    trees along the roads."""
    canvas = _Canvas(rng, width, loop, Surface.DIRT_ROAD, knobs["tree_size"])
    road = knobs["road"]
    fields = tuple(Surface[name.upper()] for name in knobs["fields"])
    farms, orchards = knobs["farm_share"], knobs["farm_share"] + knobs["orchard_share"]
    for top, bottom, left, right in grid(width, loop, knobs["block"]):
        block = (top + road, bottom, left + road, right)
        for lot in lots(rng, block, knobs["lot"]):
            roll = rng.random()
            if roll < farms:
                _farm(canvas, lot)
            elif roll < orchards:
                _orchard(canvas, lot)
            else:
                canvas.fill(lot, rng.choice(fields), rng.randrange(256))
                if rng.random() < knobs["hedge_share"]:
                    _hedges(canvas, lot)
        for _ in range(rng.randrange(3)):  # a few trees along the road
            x = rng.uniform(left + road, right)
            canvas.tree(x, top + road + 0.012)
    return canvas.layout()


def _farm(canvas: _Canvas, lot: Rect) -> None:
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


def _orchard(canvas: _Canvas, lot: Rect) -> None:
    canvas.fill(lot, Surface.PASTURE, canvas.rng.randrange(256))
    top, bottom, left, right = shrink(lot, 0.02)
    spacing = 0.042
    for row in range(int((bottom - top) / spacing) + 1):
        for column in range(int((right - left) / spacing) + 1):
            canvas.tree(left + column * spacing, top + row * spacing, 0.026)


def _hedges(canvas: _Canvas, lot: Rect) -> None:
    top, bottom, left, right = lot
    thick, height = 0.01, 0.014
    for rect in (
        (top, top + thick, left, right),
        (bottom - thick, bottom, left, right),
        (top + thick, bottom - thick, left, left + thick),
        (top + thick, bottom - thick, right - thick, right),
    ):
        canvas.add("hedge", rect, height)


def place(props: list[Prop], heights: NDArray[np.float64], step_x: float, step_y: float) -> list[Prop]:
    """The props standing on the relief: each one's base is the lowest ground under its footprint (it's sunk a
    little into slopes rather than floating)."""
    rows, columns = heights.shape
    placed = []
    for prop in props:
        xs = np.clip(np.round(np.array([-0.5, 0.0, 0.5]) * prop.width / step_x + prop.x / step_x), 0, columns - 1)
        ys = np.round(np.array([-0.5, 0.0, 0.5]) * prop.length / step_y + prop.y / step_y) % rows
        base = float(np.min(heights[np.ix_(ys.astype(np.int64), xs.astype(np.int64))]))
        placed.append(replace(prop, base=base))
    return placed


def occluders(props: list[Prop], heights: NDArray[np.float64], step_x: float, step_y: float) -> NDArray[np.float64]:
    """The ground's heights with the props standing on it: what casts shadows and makes hollows (relief.py)."""
    result = heights.copy()
    rows, columns = heights.shape
    for prop in props:
        shrink_by = 0.8 if prop.kind in ("tree", "tank", "silo", "stack") else 1.0  # round ones
        half_x, half_y = prop.width * shrink_by / 2, prop.length * shrink_by / 2
        first_column = max(int(np.ceil((prop.x - half_x) / step_x)), 0)
        last_column = min(int(np.floor((prop.x + half_x) / step_x)), columns - 1)
        first_row = int(np.ceil((prop.y - half_y) / step_y))
        last_row = int(np.floor((prop.y + half_y) / step_y))
        if last_column < first_column or last_row < first_row:
            continue
        picked = np.arange(first_row, last_row + 1) % rows
        top = prop.base + prop.height
        area = np.ix_(picked, np.arange(first_column, last_column + 1))
        result[area] = np.maximum(result[area], top)
    return result


SETTLEMENTS: dict[str, SettlementGenerator] = {"city": city, "refinery": refinery, "farmland": farmland}
# The numbers each settlement needs (settlement.layout in the scenery).
KNOBS: dict[str, tuple[str, ...]] = {
    "city": (
        "block",
        "street",
        "alley",
        "alley_share",
        "lot",
        "sidewalk",
        "park_share",
        "tower_share",
        "midrise_share",
        "tower",
        "midrise",
        "lowrise",
        "tree_size",
    ),
    "refinery": ("block", "road", "lot", "units"),
    "farmland": ("block", "road", "lot", "farm_share", "orchard_share", "hedge_share", "fields", "tree_size"),
}
