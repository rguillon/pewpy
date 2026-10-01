"""Built-up grounds on a smooth relief (relief.py): what every settlement is; each one is in grounds/ (the city, the
refinery, the farmland).

A layout is what the ground is covered with, as a surface map painted by the ground shader (streets, pavements,
yards, fields...), plus the props standing on it: buildings, tanks, stacks, pipe racks, houses, barns, silos, trees,
hedges, greenhouses, cooling towers. props/ builds the props, ground_shader.py draws both.

Each settlement's numbers (block sizes, shares, building heights...) come from the level's scenery (`layout`, see
params.py). Positions are in world units: x from the ground's left edge, y down the loop (like the relief's rows); the
layout loops along y like the rest of the ground (the grids of blocks divide the loop exactly and nothing crosses its
end). The canvas and the helpers below are shared by the settlements. Independent from Panda3D.
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from enum import IntEnum
from itertools import pairwise
from typing import ClassVar

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
    """Something standing on the ground. `kind`: "building", "house", "barn", "silo", "greenhouse", "tank",
    "plant", "stack", "pipes", "cooling_tower", "tree", "hedge", "palm" or "dead_tree"; `seed` picks its variant,
    colors and details (see props/).
    """

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


class Settlement(ABC):
    """A kind of built-up ground: its layout."""

    knobs: ClassVar[tuple[str, ...]]  # the numbers it needs (settlement.layout in the scenery)

    @abstractmethod
    def layout(self, rng: random.Random, width: float, loop: float, knobs: Knobs) -> Layout:
        """The layout of a ground `width` wide whose loop is `loop` long (world units)."""


class Canvas:
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


def place(props: list[Prop], heights: NDArray[np.float64], step_x: float, step_y: float) -> list[Prop]:
    """The props standing on the relief: each one's base is the lowest ground under its footprint (it's sunk a
    little into slopes rather than floating).
    """
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
        shrink_by = 0.8 if prop.kind in ("tree", "tank", "silo", "stack", "cooling_tower") else 1.0  # round ones
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
