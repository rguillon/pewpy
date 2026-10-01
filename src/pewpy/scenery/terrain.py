"""Voxel grounds scrolling under the ship: hills, cities, islands in a sea... (see background.py).

A ground is a seamless loop of strips of voxel columns. Each kind of ground ("biome") has a generator that
makes the column heights, plus per column a "kind" number (what the column is: a street, a tree, lava...) and,
for grounds with water, how shallow the water is. models.py colors the voxels; background_view.py draws them.
Independent from Panda3D.
"""

import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from itertools import pairwise

import numpy as np

from pewpy import config
from pewpy.scenery import landscapes, relief, settlement
from pewpy.scenery.landscapes import Flora
from pewpy.scenery.relief import RELIEF_STEP, Relief, ReliefGenerator
from pewpy.scenery.settlement import Layout, Prop, SettlementGenerator

GROUND_DEPTH = 0.35  # the base layer of the hills; they rise towards the camera, staying behind the ships
# How fast the ground seems to move on screen, as a fraction of the level's scroll speed. Kept away from the
# enemies' speeds (as fractions of level 2's scroll speed: parked Snipers 0, Gunships 0.6, Turrets 1.0,
# Drones 1.2, Weavers 1.4), or they look like they sit on the ground. Turrets slide over it too.
GROUND_SPEED = 0.3
GROUND_VOXEL = 0.07  # default size of a ground voxel; a level can pick another (`ground_voxel`)
# The shapes below are for GROUND_VOXEL; with smaller voxels the same landscape is made of more of them.
GROUND_MAX_HEIGHT = 3  # voxels above the base layer
GROUND_CHUNK_ROWS = 12  # the ground is drawn in strips of this many rows...
GROUND_CHUNKS = 5  # ...and loops after this many strips (more if the screen needs it)

# The city sits deeper than the hills so its towers can be tall without reaching the ships.
CITY_DEPTH = 0.7
CITY_MAX_HEIGHT = 0.55  # tallest tower, world units above the streets
CITY_BLOCK = 0.6  # distance from one street to the next, world units (about: the grid must loop)
CITY_STREET = 0.12  # street width, world units

SEA_DEPTH = 0.5  # the sea surface; islands rise towards the camera
ISLAND_MAX_HEIGHT = 0.28  # highest peak, world units above the sea
ISLAND_SHARE = 0.22  # share of the sea covered by land
SHALLOWS = 0.15  # how far from the coasts the water gets lighter (in noise values, 0 to 1)


@dataclass(frozen=True)
class Area:
    """A rectangle on a background layer, in world units (X right, Z up the screen)."""

    left: float
    right: float
    bottom: float
    top: float

    @classmethod
    def play_area(cls) -> "Area":
        half_width, half_height = config.PLAY_WIDTH / 2, config.PLAY_HEIGHT / 2
        return cls(-half_width, half_width, -half_height, half_height)

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom


class Kind(IntEnum):
    """What a ground column is, for its colors (see models.py). The city numbers its buildings instead, and the
    refinery adds 100 times its building number to the kind (each building gets its own shade)."""

    PLAIN = 0
    SAND = 1
    ROCK = 2
    GRASS = 3
    TREE = 4
    PALM = 5
    LAVA = 6
    EMBER = 7  # glowing cracks next to lava
    ICE = 8
    BERG = 9
    MUD = 10
    REED = 11
    DEAD_TREE = 12
    CLOUD = 13
    ROAD = 14
    WHEAT = 15
    CROP = 16
    PLOWED = 17
    LAVENDER = 18
    HEDGE = 19
    HOUSE = 20
    SILO = 21
    YARD = 22
    PIPE = 23
    TANK = 24
    STACK = 25
    PLANT = 26
    TREE_DARK = 27
    TREE_LIGHT = 28


@dataclass
class Ground:
    """What a generator makes: `heights[row][column]` in voxels (for grounds with water, 0 is water; below 0
    is nothing at all, like the gaps between clouds), `kinds[row][column]` (see Kind) and, for grounds with water,
    `shallows[row][column]` from 0 (deep) to 1 (at the coasts and on land)."""

    heights: list[list[int]]
    kinds: list[list[int]]
    shallows: list[list[float]]


# (rng, columns, rows, voxel size, highest column in voxels) -> Ground; the rows loop.
Generator = Callable[[random.Random, int, int, float, int], Ground]


@dataclass(frozen=True)
class Biome:
    """A kind of ground: how it's made and how it looks around it."""

    generate: Generator
    depth: float  # the ground's base layer; columns rise towards the camera from there
    max_height: float  # highest column, world units: keep depth - max_height > 0.1 so it stays behind the ships
    water: bool = False  # height 0 is water (a flat animated surface), not a voxel
    haze: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)  # air color, and how much of it far away
    sky: tuple[float, float, float, float] | None = None  # shows where nothing is drawn (None: the space color)
    look: str = "ground"  # how shiny it is, see background_view.py
    relief: ReliefGenerator | None = None  # a smooth ground (relief.py) instead of voxel columns
    settlement: SettlementGenerator | None = None  # on a smooth ground: streets or fields, and props (settlement.py)
    fluid: str | None = None  # on a smooth ground, what's below height 0: "water", "lava" or "gap" (see relief.py)
    flora: Flora | None = None  # on a smooth ground: sparse props placed from its shape (landscapes.py)


class Terrain:
    """A voxel ground: a seamless loop of strips ("chunks") of column heights, scrolling down.

    Row 0 is the top of the loop, and the last row joins back onto row 0. The loop is longer than the screen (it
    gets more chunks if needed), so each chunk shows at most once. See Ground for heights, kinds and shallows.
    """

    def __init__(
        self,
        area: Area,
        speed_factor: float,
        seed: int | None = None,
        voxel: float = GROUND_VOXEL,
        biome: str = "planet",
    ) -> None:
        self.rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        self.area = area
        self.speed_factor = speed_factor
        self.voxel = voxel
        self.biome = biome
        settings = BIOMES[biome]
        self.depth = settings.depth
        self.water = settings.water
        scale = GROUND_VOXEL / voxel  # how many voxels for one default-size voxel, along each side
        self.chunk_rows_count = round(GROUND_CHUNK_ROWS * scale)
        self.chunk_height = self.chunk_rows_count * self.voxel
        self.chunks = max(GROUND_CHUNKS, math.ceil(area.height / self.chunk_height) + 1)
        self.columns = math.ceil(area.width / self.voxel) + 1
        self.rows = self.chunk_rows_count * self.chunks
        self.loop_length = self.rows * self.voxel
        self.max_height = round(settings.max_height / voxel)
        ground = settings.generate(self.rng, self.columns, self.rows, voxel, self.max_height)
        self.heights, self.kinds, self.shallows = ground.heights, ground.kinds, ground.shallows
        self.offset = 0.0  # how far the ground has scrolled, in world units
        self.relief: Relief | None = None
        self.relief_rows = 0  # rows of the relief per chunk
        self.layout: Layout | None = None
        self.props: list[Prop] = []  # standing on the relief
        if settings.relief is not None:
            self.relief_rows = max(round(self.chunk_height / RELIEF_STEP), 1)
            step_y = self.chunk_height / self.relief_rows
            columns = math.ceil(self.columns * voxel / RELIEF_STEP) + 1
            rng = np.random.default_rng(self.rng.randrange(2**32))
            shape = settings.relief(rng, self.relief_rows * self.chunks, columns, settings.max_height, step_y)
            surface = np.maximum(shape.heights, 0.0) if settings.fluid else shape.heights
            props = []
            if settings.settlement is not None:
                self.layout = settings.settlement(self.rng, (columns - 1) * RELIEF_STEP, self.loop_length)
                props += self.layout.props
            if settings.flora is not None:
                props += settings.flora(self.rng, shape, RELIEF_STEP, step_y)
            occluders = None
            if props:
                self.props = settlement.place(props, surface, RELIEF_STEP, step_y)
                occluders = settlement.occluders(self.props, surface, RELIEF_STEP, step_y)
            self.relief = relief.make_relief(shape, RELIEF_STEP, step_y, occluders, fluid=settings.fluid is not None)

    def update(self, dt: float, scroll_speed: float) -> None:
        self.offset = (self.offset + scroll_speed * self.speed_factor * dt) % self.loop_length

    def chunk_rows(self, chunk: int) -> list[list[int]]:
        start = chunk * self.chunk_rows_count
        return self.heights[start : start + self.chunk_rows_count]

    def chunk_kinds(self, chunk: int) -> list[list[int]]:
        start = chunk * self.chunk_rows_count
        return self.kinds[start : start + self.chunk_rows_count]

    def chunk_shallows(self, chunk: int) -> list[list[float]]:
        """The chunk's rows of `shallows`, plus the next chunk's first row (the water surface's bottom edge)."""
        start = chunk * self.chunk_rows_count
        return [self.shallows[(start + row) % self.rows] for row in range(self.chunk_rows_count + 1)]

    def chunk_props(self, chunk: int) -> list[Prop]:
        """The props standing in a chunk (by the middle of their footprint)."""
        start = chunk * self.chunk_height
        return [prop for prop in self.props if start <= prop.y < start + self.chunk_height]

    def chunk_top(self, chunk: int) -> float:
        """World Z of the top edge of a chunk."""
        start = self.area.top + self.chunk_height
        return start - (chunk * self.chunk_height + self.offset) % self.loop_length

    @property
    def left(self) -> float:
        """World X of the left edge of the first column (the ground is centered)."""
        return -self.columns * self.voxel / 2


def _ground_heights(rng: random.Random, columns: int, rows: int, scale: float, max_height: int) -> list[list[int]]:
    """Rolling hills (two octaves of smooth noise, looping along the rows) with a few craters.

    Sizes are in default-size voxels, times `scale` when the voxels are smaller.
    """
    coarse = _Noise(rng, columns, rows, cell=round(9 * scale))
    fine = _Noise(rng, columns, rows, cell=round(4 * scale))
    craters = [
        (rng.uniform(0, columns), rng.uniform(0, rows), rng.uniform(2.0, 4.5) * scale)
        for _ in range(round(rows / (12 * scale)))
    ]
    heights = []
    for row in range(rows):
        line = []
        for column in range(columns):
            value = 0.7 * coarse.at(column, row) + 0.3 * fine.at(column, row)
            for crater_x, crater_y, radius in craters:
                dy = min(abs(row - crater_y), rows - abs(row - crater_y))  # the loop wraps along rows
                distance = math.hypot(column - crater_x, dy) / radius
                if distance < 1:
                    value -= 0.6 * (1 - distance * distance)  # bowl
                elif distance < 1.3:
                    value += 0.25  # rim
            line.append(max(0, min(max_height, int(value * (max_height + 1)))))
        heights.append(line)
    return heights


def _islands(
    rng: random.Random, columns: int, rows: int, scale: float, max_height: int
) -> tuple[list[list[int]], list[list[float]]]:
    """Islands in a sea: (heights, shallows). Land where smooth noise is high, rising towards the middle of each
    island; the water gets shallower near the coasts. Loops along the rows.

    The sea level is picked so that ISLAND_SHARE of the map is land, whatever the random values.
    """
    coarse = _Noise(rng, columns, rows, cell=round(11 * scale))
    fine = _Noise(rng, columns, rows, cell=round(5 * scale))
    values = [
        [0.7 * coarse.at(column, row) + 0.3 * fine.at(column, row) for column in range(columns)] for row in range(rows)
    ]
    ordered = sorted(value for line in values for value in line)
    sea_level = ordered[min(len(ordered) - 1, int(len(ordered) * (1 - ISLAND_SHARE)))]
    peak = ordered[-1]
    heights, shallows = [], []
    for line in values:
        heights.append([
            min(max_height, 1 + int((value - sea_level) / max(peak - sea_level, 1e-9) * max_height))
            if value > sea_level
            else 0
            for value in line
        ])
        shallows.append([min(1.0, max(0.0, 1 - (sea_level - value) / SHALLOWS)) for value in line])
    return heights, shallows


def _city(
    rng: random.Random, columns: int, rows: int, voxel: float, max_height: int
) -> tuple[list[list[int]], list[list[int]]]:
    """Blocks of buildings between streets. Returns (heights, lots): each block is split into 1 to 3 lots
    along each side, each lot is one building (numbered from 1) of its own height; streets are 0.

    The street grid loops along the rows like the rest of the ground.
    """
    street = max(1, round(CITY_STREET / voxel))

    def cuts(length: int) -> list[int]:
        count = max(1, round(length * voxel / CITY_BLOCK))
        return [round(i * length / count) for i in range(count + 1)]

    heights = [[0] * columns for _ in range(rows)]
    lots = [[0] * columns for _ in range(rows)]
    row_cuts, column_cuts = cuts(rows), cuts(columns)
    lot = 0
    for top, bottom in pairwise(row_cuts):
        for left, right in pairwise(column_cuts):
            # The street runs along the top and left of each block.
            for lot_top, lot_bottom in _split(rng, top + street, bottom):
                for lot_left, lot_right in _split(rng, left + street, right):
                    lot += 1
                    height = _building_height(rng, max_height)
                    for row in range(lot_top, lot_bottom):
                        for column in range(lot_left, lot_right):
                            heights[row][column] = height
                            lots[row][column] = lot
    return heights, lots


def _split(rng: random.Random, start: int, end: int) -> list[tuple[int, int]]:
    """Cut [start, end) into 1 to 3 pieces, each at least 2 long."""
    pieces = rng.choice((1, 2, 2, 3))
    while pieces > 1 and (end - start) < 2 * pieces:
        pieces -= 1
    edges = sorted(rng.sample(range(start + 2, end - 1), pieces - 1)) if pieces > 1 else []
    bounds = [start, *edges, end]
    return [(a, b) for a, b in pairwise(bounds) if b > a]


def _building_height(rng: random.Random, max_height: int) -> int:
    """Mostly low and mid-rise buildings, a few towers, some empty lots (plazas)."""
    roll = rng.random()
    if roll < 0.08:
        return 0
    if roll < 0.7:
        return rng.randint(max(1, max_height // 6), max(1, max_height // 3))
    if roll < 0.93:
        return rng.randint(max(1, max_height // 3), max(1, 2 * max_height // 3))
    return rng.randint(max(1, 2 * max_height // 3), max_height)


class _Noise:
    """Smooth value noise between random values on a coarse grid; loops along the rows."""

    def __init__(self, rng: random.Random, columns: int, rows: int, cell: int) -> None:
        self.cell = cell
        self.grid_rows = max(1, round(rows / cell))
        self.row_scale = self.grid_rows / rows  # stretch so the grid loops exactly with the rows
        grid_columns = columns // cell + 2
        self.values = [[rng.random() for _ in range(grid_columns)] for _ in range(self.grid_rows)]

    def at(self, column: float, row: float) -> float:
        x, y = column / self.cell, row * self.row_scale
        x0, y0 = int(x), int(y)
        tx, ty = _smooth(x - x0), _smooth(y - y0)
        top, bottom = self.values[y0 % self.grid_rows], self.values[(y0 + 1) % self.grid_rows]
        upper = top[x0] + (top[x0 + 1] - top[x0]) * tx
        lower = bottom[x0] + (bottom[x0 + 1] - bottom[x0]) * tx
        return upper + (lower - upper) * ty


def _smooth(t: float) -> float:
    return t * t * (3 - 2 * t)


# --- Generators, one per biome. Sizes are in default-size voxels, times `scale` when the voxels are smaller. ---


def _scale(voxel: float) -> float:
    return GROUND_VOXEL / voxel


def _empty(columns: int, rows: int, height: int = 0, kind: int = Kind.PLAIN) -> Ground:
    return Ground(
        [[height] * columns for _ in range(rows)],
        [[kind] * columns for _ in range(rows)],
        [[1.0] * columns for _ in range(rows)],
    )


def _hills(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    ground = _empty(columns, rows)
    ground.heights = _ground_heights(rng, columns, rows, _scale(voxel), max_height)
    return ground


def _city_ground(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    ground = _empty(columns, rows)
    ground.heights, ground.kinds = _city(rng, columns, rows, voxel, max_height)
    return ground


def _islands_ground(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    ground = _empty(columns, rows)
    ground.heights, ground.shallows = _islands(rng, columns, rows, _scale(voxel), max_height)
    return ground


def _threshold(values: list[list[float]], share: float) -> tuple[float, float]:
    """(the value above which `share` of all values are, the highest value)."""
    ordered = sorted(value for line in values for value in line)
    return ordered[min(len(ordered) - 1, int(len(ordered) * (1 - share)))], ordered[-1]


def _two_octaves(rng: random.Random, columns: int, rows: int, coarse: float, fine: float) -> list[list[float]]:
    big, small = _Noise(rng, columns, rows, cell=round(coarse)), _Noise(rng, columns, rows, cell=round(fine))
    return [
        [0.7 * big.at(column, row) + 0.3 * small.at(column, row) for column in range(columns)] for row in range(rows)
    ]


def _desert(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """Dunes in long ridges, flat-topped rock mesas, and a few oasis pools ringed with grass and palms."""
    scale = _scale(voxel)
    warp = _Noise(rng, columns, rows, cell=round(10 * scale))
    mesas = _Noise(rng, columns, rows, cell=round(15 * scale))
    pools = _Noise(rng, columns, rows, cell=round(8 * scale))
    crests = max(1, round(rows / (8 * scale)))  # dune ridges per loop: a whole number, so they loop too
    palm = max(2, round(0.12 / voxel))
    ground = _empty(columns, rows)
    for row in range(rows):
        for column in range(columns):
            phase = 2 * math.pi * crests * row / rows + 0.1 * column / scale + 4 * warp.at(column, row)
            height, kind, shallow = 1 + int((0.5 + 0.5 * math.sin(phase)) ** 2 * 0.35 * max_height), Kind.SAND, 1.0
            mesa, pool = mesas.at(column, row), pools.at(column, row)
            if mesa > 0.8:
                height, kind = max_height, Kind.ROCK
            elif mesa > 0.77:
                height, kind = max(height, round(0.6 * max_height)), Kind.ROCK
            elif pool < 0.14:
                height, shallow = 0, max(0.0, 1 - (0.14 - pool) / 0.06)
            elif pool < 0.19:
                height, kind = (palm, Kind.PALM) if rng.random() < 0.08 else (1, Kind.GRASS)
            ground.heights[row][column], ground.kinds[row][column] = height, kind
            ground.shallows[row][column] = shallow
    return ground


def _meander(rng: random.Random, columns: int, rows: int, spacing: float, swing: float) -> Callable[[float], float]:
    """A river's middle column for each row: winds from side to side, a whole number of times per loop."""
    bends = max(1, round(rows / spacing))
    phase = rng.uniform(0, 2 * math.pi)

    def middle(row: float) -> float:
        turn = 2 * math.pi * bends * row / rows + phase
        return columns * (0.5 + swing * math.sin(turn) + 0.05 * math.sin(3 * turn))

    return middle


def _forest(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """A canopy of round treetops in three greens, some clearings, and a river winding through."""
    scale = _scale(voxel)
    ground = _empty(columns, rows, height=1, kind=Kind.GRASS)
    river, half_width = _meander(rng, columns, rows, 40 * scale, 0.3), 1.8 * scale
    for row in range(rows):
        for column in range(columns):
            distance = abs(column + 0.5 - river(row))
            if distance < half_width:
                ground.heights[row][column], ground.shallows[row][column] = 0, distance / half_width
    clearings = _Noise(rng, columns, rows, cell=round(12 * scale))
    step = max(2, round(2.6 * scale))
    for top_row in range(0, rows, step):
        for left in range(0, columns, step):
            middle_row, middle_column = top_row + rng.uniform(0, step), left + rng.uniform(0, step)
            if clearings.at(min(middle_column, columns - 1), middle_row) > 0.64:
                continue
            radius = rng.uniform(1.0, 1.8) * scale
            top = rng.randint(max(2, max_height // 2), max(2, max_height))
            _dome(
                ground, middle_column, middle_row, radius, top, rng.choice((Kind.TREE, Kind.TREE_DARK, Kind.TREE_LIGHT))
            )
    return ground


def _dome(ground: Ground, middle_column: float, middle_row: float, radius: float, top: int, kind: int) -> None:
    """A round top (tree, iceberg...) on land: raises columns within `radius`, highest in the middle."""
    rows, columns = len(ground.heights), len(ground.heights[0])
    for row in range(int(middle_row - radius) - 1, int(middle_row + radius) + 2):
        for column in range(max(0, int(middle_column - radius) - 1), min(columns, int(middle_column + radius) + 2)):
            distance = math.hypot(column + 0.5 - middle_column, row + 0.5 - middle_row) / radius
            line = row % rows
            if distance > 1 or ground.heights[line][column] <= 0:
                continue  # not on water
            height = 1 + round((top - 1) * math.sqrt(1 - distance * distance))
            if height > ground.heights[line][column]:
                ground.heights[line][column], ground.kinds[line][column] = height, kind


def _canyon(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """A plateau cut by a winding canyon: stepped cliffs in rock layers, sandbanks, a river at the bottom."""
    scale = _scale(voxel)
    ground = _empty(columns, rows)
    top = _Noise(rng, columns, rows, cell=round(10 * scale))
    river = _meander(rng, columns, rows, 45 * scale, 0.22)
    water, floor, wall, steps = 1.6 * scale, 3.1 * scale, 7 * scale, 4
    for row in range(rows):
        for column in range(columns):
            distance = abs(column + 0.5 - river(row))
            plateau = max_height - int(top.at(column, row) * 0.2 * max_height)
            if distance < water:
                height, kind = 0, Kind.PLAIN
                ground.shallows[row][column] = distance / water
            elif distance < floor:
                height, kind = 1, Kind.SAND
            elif distance < floor + wall:  # terraces
                height, kind = max(1, round(plateau * math.ceil((distance - floor) / wall * steps) / steps)), Kind.ROCK
            else:
                height, kind = plateau, Kind.ROCK
                if rng.random() < 0.03:
                    height, kind = plateau + 1, Kind.GRASS  # scrub
            ground.heights[row][column], ground.kinds[row][column] = min(height, max_height), kind
    return ground


FIELDS = (Kind.WHEAT, Kind.WHEAT, Kind.CROP, Kind.CROP, Kind.PLOWED, Kind.LAVENDER)


def _farmland(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """Patchwork fields between dirt roads (wheat, green crops, plowed earth, lavender), some with hedges
    around, orchards, and farms with a house and a silo."""
    road = max(1, round(0.05 / voxel))
    ground = _empty(columns, rows, kind=Kind.ROAD)
    for top, bottom, left, right in _blocks(columns, rows, voxel, 0.5):
        for lot_top, lot_bottom in _split(rng, top + road, bottom):
            for lot_left, lot_right in _split(rng, left + road, right):
                roll = rng.random()
                lot = (lot_top, lot_bottom, lot_left, lot_right)
                if roll < 0.12:
                    _farm(ground, lot, voxel, max_height)
                elif roll < 0.25:
                    _fill(ground, lot, 0, Kind.GRASS)
                    for row in range(lot_top + 1, lot_bottom, 2):  # orchard rows
                        for column in range(lot_left + 1, lot_right, 2):
                            ground.heights[row % rows][column], ground.kinds[row % rows][column] = 2, Kind.TREE
                else:
                    _fill(ground, lot, 0, rng.choice(FIELDS))
                    if rng.random() < 0.5:
                        _border(ground, lot, 1, Kind.HEDGE)
    return ground


def _blocks(columns: int, rows: int, voxel: float, size: float) -> list[tuple[int, int, int, int]]:
    """(top, bottom, left, right) of a grid of blocks about `size` world units wide, looping along the rows."""

    def cuts(length: int) -> list[int]:
        count = max(1, round(length * voxel / size))
        return [round(i * length / count) for i in range(count + 1)]

    return [
        (top, bottom, left, right) for top, bottom in pairwise(cuts(rows)) for left, right in pairwise(cuts(columns))
    ]


def _fill(ground: Ground, lot: tuple[int, int, int, int], height: int, kind: int) -> None:
    """Set the cells of `lot` (top, bottom, left, right; the ends excluded), the parts within the ground only: a
    feature placed near the edge (a stack in a small yard) may reach past it."""
    top, bottom, left, right = _within(ground, lot)
    for row in range(top, bottom):
        for column in range(left, right):
            ground.heights[row][column], ground.kinds[row][column] = height, kind


def _border(ground: Ground, lot: tuple[int, int, int, int], height: int, kind: int) -> None:
    top, bottom, left, right = lot
    first_row, end_row, first_column, end_column = _within(ground, lot)
    for row in range(first_row, end_row):
        for column in range(first_column, end_column):
            if row in (top, bottom - 1) or column in (left, right - 1):
                ground.heights[row][column], ground.kinds[row][column] = height, kind


def _within(ground: Ground, lot: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    top, bottom, left, right = lot
    rows, columns = len(ground.heights), len(ground.heights[0]) if ground.heights else 0
    return max(top, 0), min(bottom, rows), max(left, 0), min(right, columns)


def _farm(ground: Ground, lot: tuple[int, int, int, int], voxel: float, max_height: int) -> None:
    top, bottom, left, right = lot
    _fill(ground, lot, 0, Kind.GRASS)
    house = (top + 1, min(bottom, top + 4), left + 1, min(right, left + 5))
    _fill(ground, house, min(max_height, round(0.08 / voxel)), Kind.HOUSE)
    if right - left > 7 and bottom - top > 3:
        silo = (top + 1, top + 3, right - 3, right - 1)
        _fill(ground, silo, min(max_height, round(0.16 / voxel)), Kind.SILO)


def _pack_ice(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """A dark cold sea covered in flat ice floes, with a few tall icebergs."""
    scale = _scale(voxel)
    values = _two_octaves(rng, columns, rows, 7 * scale, 3 * scale)
    sea_level, peak = _threshold(values, 0.4)
    berg_level = _threshold(values, 0.03)[0]
    ground = _empty(columns, rows)
    for row, line in enumerate(values):
        for column, value in enumerate(line):
            if value > berg_level:
                rise = (value - berg_level) / max(peak - berg_level, 1e-9)
                ground.heights[row][column], ground.kinds[row][column] = 2 + int(rise * (max_height - 2)), Kind.BERG
            elif value > sea_level:
                ground.heights[row][column], ground.kinds[row][column] = 1, Kind.ICE
            else:
                ground.shallows[row][column] = max(0.0, 1 - (sea_level - value) / 0.08)
    return ground


def _swamp(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """Murky water full of small muddy islets with reeds and a few dead trees."""
    scale = _scale(voxel)
    values = _two_octaves(rng, columns, rows, 6 * scale, 2.5 * scale)
    sea_level, _ = _threshold(values, 0.45)
    ground = _empty(columns, rows)
    for row, line in enumerate(values):
        for column, value in enumerate(line):
            if value <= sea_level:
                ground.shallows[row][column] = max(0.0, 1 - (sea_level - value) / 0.1)
            elif rng.random() < 0.012:
                tree = rng.randint(max(2, max_height // 2), max(2, max_height))
                ground.heights[row][column], ground.kinds[row][column] = tree, Kind.DEAD_TREE
            elif value > sea_level + 0.06 and rng.random() < 0.3:
                ground.heights[row][column], ground.kinds[row][column] = 2, Kind.REED
            else:
                ground.heights[row][column], ground.kinds[row][column] = 1, Kind.MUD
    return ground


def _volcano(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """Black volcanic hills with rivers and pools of glowing lava, and glowing cracks along them."""
    scale = _scale(voxel)
    values = _two_octaves(rng, columns, rows, 11 * scale, 4 * scale)
    rivers = _Noise(rng, columns, rows, cell=round(9 * scale))
    ground = _empty(columns, rows, kind=Kind.ROCK)
    for row, line in enumerate(values):
        for column, value in enumerate(line):
            if abs(rivers.at(column, row) - 0.5) < 0.03 or value < 0.25:
                ground.kinds[row][column] = Kind.LAVA  # height 0
            else:
                ground.heights[row][column] = 1 + int(value**1.4 * max_height)
    for row in range(rows):
        for column in range(columns):
            if ground.kinds[row][column] != Kind.LAVA:
                near = [(row + dr) % rows for dr in (-1, 1)], [c for c in (column - 1, column + 1) if 0 <= c < columns]
                lava_rows, lava_columns = near
                if any(ground.kinds[r][column] == Kind.LAVA for r in lava_rows) or any(
                    ground.kinds[row][c] == Kind.LAVA for c in lava_columns
                ):
                    ground.kinds[row][column] = Kind.EMBER
    return ground


TOWN_LIGHT = -2  # in the clouds' gaps: a light on the ground far below (see ground_look.py)


def _clouds(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """A sea of low, flat clouds at night with gaps: nothing is drawn there, the dark ground far below shows."""
    scale = _scale(voxel)
    values = _two_octaves(rng, columns, rows, 13 * scale, 4 * scale)
    cover, peak = _threshold(values, 0.6)
    ground = _empty(columns, rows, kind=Kind.CLOUD)
    for row, line in enumerate(values):
        for column, value in enumerate(line):
            if value > cover:
                # Round puffs: they rise fast from the edges, then flatten out on top.
                ground.heights[row][column] = int(((value - cover) / max(peak - cover, 1e-9)) ** 0.4 * max_height)
            elif rng.random() < 0.025:
                ground.heights[row][column] = TOWN_LIGHT  # a gap, with a light far below
            else:
                ground.heights[row][column] = -1  # a gap
    return ground


def _refinery(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """A refinery at night: round tanks, pipe yards, plants with glowing furnaces, tall stacks with flames."""
    road = max(1, round(0.08 / voxel))
    ground = _empty(columns, rows, kind=Kind.ROAD)
    lot = 0
    for top, bottom, left, right in _blocks(columns, rows, voxel, 0.55):
        for lot_top, lot_bottom in _split(rng, top + road, bottom):
            for lot_left, lot_right in _split(rng, left + road, right):
                lot += 1
                bounds = (lot_top, lot_bottom, lot_left, lot_right)
                _fill(ground, bounds, 0, Kind.YARD + 100 * lot)
                _refinery_lot(
                    ground,
                    bounds,
                    rng.choice((Kind.TANK, Kind.TANK, Kind.PLANT, Kind.STACK, Kind.PIPE)),
                    lot,
                    rng,
                    max_height,
                )
    return ground


def _refinery_lot(
    ground: Ground, lot: tuple[int, int, int, int], kind: Kind, number: int, rng: random.Random, max_height: int
) -> None:
    top, bottom, left, right = lot
    tag = 100 * number
    if kind == Kind.PIPE:
        for row in range(top + 1, bottom, 3):
            for column in range(left, right):
                ground.heights[row][column], ground.kinds[row][column] = 1, Kind.PIPE + tag
    elif kind == Kind.TANK:
        middle_row, middle_column = (top + bottom) / 2, (left + right) / 2
        radius = min(bottom - top, right - left) / 2 - 0.3
        height = rng.randint(max(1, max_height // 4), max(1, max_height // 2))
        for row in range(top, bottom):
            for column in range(left, right):
                if math.hypot(row + 0.5 - middle_row, column + 0.5 - middle_column) <= radius:
                    ground.heights[row][column], ground.kinds[row][column] = height, Kind.TANK + tag
    elif kind == Kind.PLANT:
        inner = (top + 1, max(top + 2, bottom - 1), left + 1, max(left + 2, right - 1))
        _fill(ground, inner, rng.randint(max(1, max_height // 4), max(1, max_height // 2)), Kind.PLANT + tag)
    else:  # a stack in the middle of a yard
        row, column = (top + bottom) // 2, (left + right) // 2
        _fill(
            ground,
            (row, row + 2, column, column + 2),
            rng.randint(max(1, 2 * max_height // 3), max_height),
            Kind.STACK + tag,
        )


def _mountains(rng: random.Random, columns: int, rows: int, voxel: float, max_height: int) -> Ground:
    """Sharp mountain ridges with snowy tops, and flat glaciers in the valleys."""
    scale = _scale(voxel)
    ridges = _Noise(rng, columns, rows, cell=round(16 * scale))
    slopes, rocks = _Noise(rng, columns, rows, cell=round(6 * scale)), _Noise(rng, columns, rows, cell=round(3 * scale))
    ground = _empty(columns, rows, kind=Kind.ROCK)
    for row in range(rows):
        for column in range(columns):
            ridge = 1 - abs(2 * ridges.at(column, row) - 1)
            value = 0.65 * ridge**1.5 + 0.25 * slopes.at(column, row) + 0.1 * rocks.at(column, row)
            if value < 0.3:
                ground.heights[row][column], ground.kinds[row][column] = 1, Kind.ICE  # glacier
            else:
                ground.heights[row][column] = min(max_height, int(value * max_height * 1.2))
    return ground


BIOMES: dict[str, Biome] = {
    "planet": Biome(_hills, GROUND_DEPTH, GROUND_MAX_HEIGHT * GROUND_VOXEL, relief=landscapes.hills),
    "city": Biome(
        _city_ground,
        CITY_DEPTH,
        CITY_MAX_HEIGHT,
        look="city",
        relief=landscapes.level_ground,
        settlement=settlement.city,
    ),
    "ocean": Biome(_islands_ground, SEA_DEPTH, ISLAND_MAX_HEIGHT, water=True, relief=landscapes.islands, fluid="water"),
    "desert": Biome(
        _desert,
        0.5,
        0.3,
        water=True,
        haze=(0.36, 0.27, 0.18, 0.45),
        look="matte",
        relief=landscapes.desert,
        fluid="water",
        flora=landscapes.palms,
    ),
    "forest": Biome(
        _forest, 0.45, 0.25, water=True, haze=(0.3, 0.36, 0.34, 0.45), relief=landscapes.forest, fluid="water"
    ),
    "canyon": Biome(
        _canyon,
        0.7,
        0.5,
        water=True,
        haze=(0.36, 0.24, 0.2, 0.4),
        look="matte",
        relief=landscapes.canyon,
        fluid="water",
    ),
    "farmland": Biome(
        _farmland,
        0.35,
        0.2,
        haze=(0.34, 0.38, 0.42, 0.4),
        look="matte",
        relief=landscapes.rolling,
        settlement=settlement.farmland,
    ),
    "pack_ice": Biome(
        _pack_ice,
        0.5,
        0.3,
        water=True,
        haze=(0.36, 0.42, 0.48, 0.45),
        look="ice",
        relief=landscapes.pack_ice,
        fluid="water",
    ),
    "volcano": Biome(_volcano, 0.5, 0.3, haze=(0.2, 0.06, 0.04, 0.45), relief=landscapes.volcano, fluid="lava"),
    "swamp": Biome(
        _swamp,
        0.4,
        0.22,
        water=True,
        haze=(0.2, 0.25, 0.18, 0.5),
        relief=landscapes.swamp,
        fluid="water",
        flora=landscapes.dead_trees,
    ),
    "clouds": Biome(
        _clouds,
        0.6,
        0.12,
        haze=(0.16, 0.18, 0.26, 0.4),
        sky=(0.01, 0.03, 0.05, 1),
        look="matte",
        relief=landscapes.clouds,
        fluid="gap",
    ),
    "refinery": Biome(
        _refinery,
        0.65,
        0.5,
        haze=(0.22, 0.13, 0.07, 0.45),
        look="city",
        relief=landscapes.level_ground,
        settlement=settlement.refinery,
    ),
    "mountains": Biome(_mountains, 0.7, 0.5, haze=(0.32, 0.37, 0.45, 0.45), relief=landscapes.mountains),
}
