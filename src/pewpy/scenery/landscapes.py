"""The smooth grounds' landscapes (relief.py): the shape of each kind of ground, as heights and marks.

Every generator takes (rng, rows, columns, highest point, step, knobs) and returns a Shape, looping along the rows.
The knobs are the landscape's own numbers, from the level's scenery (see params.py and KNOBS below); sizes are in
world units (divided by the step to count grid points). Grounds with water, lava or the gaps of a
cloud deck have them below height 0 (see relief.py); the marks are for the ground shader (ground_shader.py), their
meaning depends on the landscape. A few landscapes also have sparse props, placed from their shape ("flora").

Numpy only, independent from Panda3D.
"""

import math
import random
from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from pewpy.scenery.params import Knobs
from pewpy.scenery.relief import FloatGrid, Shape, eroded_noise, periodic_noise, ridged_mountains, smoothstep
from pewpy.scenery.settlement import Prop

Generator = np.random.Generator
# (rng, rows, columns, highest point in world units, step, knobs) -> the shape
Landscape = Callable[[Generator, int, int, float, float, Knobs], Shape]
# (rng, shape, step across, step down, knobs) -> props standing on the ground
Flora = Callable[[random.Random, Shape, float, float, Knobs], list[Prop]]


def _noise(rng: Generator, rows: int, columns: int, size: float, step: float) -> FloatGrid:
    """Smooth noise, 0 to 1, about `size` world units from one bump to the next."""
    return periodic_noise(rng, rows, columns, size / step)


def _normalized(values: FloatGrid, low: float = 1.0, high: float = 99.5) -> FloatGrid:
    """Stretched to 0-1 between two percentiles (clipped beyond)."""
    bottom, top = np.percentile(values, low), np.percentile(values, high)
    return np.clip((values - bottom) / max(top - bottom, 1e-9), 0.0, 1.0)


def _level_for_share(values: FloatGrid, share: float) -> float:
    """The value above which `share` of the points lie."""
    return float(np.percentile(values, 100 * (1 - share)))


def _meander(rng: Generator, rows: int, columns: int, spacing: float, swing: float, step: float) -> FloatGrid:
    """How far each point is from a river winding down the loop (world units): it swings from side to side, a
    whole number of bends per loop.
    """
    bends = max(1, round(rows * step / spacing))
    phase = rng.uniform(0, 2 * math.pi)
    turn = 2 * math.pi * bends * np.arange(rows) / rows + phase
    middle = columns * step * (0.5 + swing * np.sin(turn) + 0.05 * np.sin(3 * turn))
    return np.abs(np.arange(columns)[None, :] * step - middle[:, None])


def _wrapped_distance(rows: int, columns: int, step: float, x: float, y: float) -> FloatGrid:
    """Distance from (x, y) to every point, the rows looping."""
    dy = np.abs(np.arange(rows) * step - y)
    dy = np.minimum(dy, rows * step - dy)
    dx = np.arange(columns) * step - x
    return np.hypot(dx[None, :], dy[:, None])


def mountains(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Eroded ranges (about `range_size` apart) with sharp crests (`crest_size`), flat valley floors between them."""
    ranges = eroded_noise(rng, rows, columns, knobs["range_size"] / step)
    crests = ridged_mountains(rng, rows, columns, knobs["crest_size"] / step, octaves=5)
    middle, top = np.percentile(ranges, 40), np.percentile(ranges, 90)
    value = ranges + 0.6 * crests * smoothstep(middle, top, ranges)  # sharp crests on the high ground only
    value = _normalized(value, 3, 99.7)  # the lowest 3 % flat: valley floors
    return Shape(max_height * value**1.4)


def rolling(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Gently rolling ground for farmland: wide low swells, `height` high (`max_height` is for what stands on it,
    not used).
    """
    swells = _noise(rng, rows, columns, knobs["swell_size"], step)
    detail = _noise(rng, rows, columns, knobs["detail_size"], step)
    return Shape(knobs["height"] * (0.7 * swells + 0.3 * detail))


def level_ground(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Nearly flat ground for the city and the refinery, just not perfectly even (`height`)."""
    return Shape(knobs["height"] * _noise(rng, rows, columns, knobs["size"], step))


def hills(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """A dusty planet: low eroded hills pocked with craters (one per `crater_spacing` of the loop). Marks: the
    craters' rims and the dust thrown out.
    """
    value = _normalized(eroded_noise(rng, rows, columns, knobs["size"] / step, octaves=6))
    rims = np.zeros_like(value)
    for _ in range(max(1, round(rows * step / knobs["crater_spacing"]))):
        radius = rng.uniform(*knobs["crater_radius"])
        distance = _wrapped_distance(rows, columns, step, rng.uniform(0, columns * step), rng.uniform(0, rows * step))
        d = distance / radius
        value -= 0.55 * np.clip(1 - d * d, 0.0, 1.0)  # the bowl
        rim = np.exp(-(((d - 1.05) / 0.18) ** 2))
        value += 0.22 * rim
        rims = np.maximum(rims, rim + 0.4 * np.exp(-d) * (d > 1))
    return Shape(max_height * np.clip(value, 0.0, 1.0), np.clip(rims, 0.0, 1.0))


def islands(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Islands in a sea (`land_share` of it), shelving into shallows around them."""
    value = 0.65 * _noise(rng, rows, columns, knobs["size"], step)
    value += 0.25 * _noise(rng, rows, columns, knobs["detail_size"], step)
    value += 0.1 * _noise(rng, rows, columns, knobs["fine_size"], step)
    sea = _level_for_share(value, knobs["land_share"])
    peak = float(np.max(value))
    land = np.clip((value - sea) / max(peak - sea, 1e-9), 0.0, 1.0) ** 0.8 * max_height
    return Shape(np.where(value > sea, land, (value - sea) * 0.7))


def desert(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Long dune ridges, flat-topped rock mesas, a few oasis pools ringed with grass (and palms, see `palms`).
    Marks: 0 sand, 0.5 the grass around the pools, 1 rock.
    """
    crests = max(1, round(rows * step / knobs["dune_spacing"]))  # dune ridges per loop: whole, so they loop too
    y = np.arange(rows)[:, None] / rows
    x = np.arange(columns)[None, :] * step
    phase = 2 * math.pi * crests * y + 1.4 * x + 4 * _noise(rng, rows, columns, 0.7, step)
    dune = (0.5 + 0.5 * np.sin(phase + 0.6 * np.sin(phase))) ** 2  # a gentle windward side, a steep slip face
    heights = 0.012 + dune * 0.3 * max_height
    mesas = _noise(rng, rows, columns, knobs["mesa_size"], step)
    rock = smoothstep(0.74, 0.77, mesas)  # edges a few grid points wide: no jagged cliffs
    heights = np.maximum(heights, 0.6 * max_height * rock)  # a ledge around each mesa...
    heights = np.maximum(heights, max_height * smoothstep(0.79, 0.83, mesas))  # ...and its flat top
    pools = _noise(rng, rows, columns, knobs["pool_size"], step)
    grass = (pools >= 0.14) & (pools < 0.19) & (rock < 0.5)  # a ring around the pool
    heights = np.where(grass, np.minimum(heights, 0.008), heights)
    heights = np.where((pools < 0.14) & (rock < 0.5), (pools - 0.14) * 0.6, heights)
    marks = np.where(rock > 0.5, 1.0, np.where(grass, 0.5, 0.0))
    return Shape(heights, marks)


def forest(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """A canopy over rolling ground, some clearings, and a river winding through. Marks: 1 under the canopy."""
    ground = 0.04 * _noise(rng, rows, columns, 1.2, step)
    canopy = smoothstep(0.66, 0.6, _noise(rng, rows, columns, knobs["canopy_size"], step))  # clearings: noise high
    river = _meander(rng, rows, columns, knobs["river_spacing"], 0.3, step)
    half_width = knobs["river_width"] / 2
    canopy *= smoothstep(half_width * 1.4, half_width * 2.2, river)  # open banks
    heights = ground + 0.045 * canopy
    heights = np.where(river < half_width, -0.005 - 0.03 * (1 - river / half_width), heights)
    return Shape(heights, canopy)


def canyon(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """A plateau cut by a winding canyon: stepped cliffs, sandbanks, a river at the bottom. Marks: 0.5 sand. The
    river, the canyon's floor and its walls reach `river`, `floor` and `floor + wall` from its middle.
    """
    plateau = max_height * (0.85 + 0.15 * _noise(rng, rows, columns, 0.7, step))
    distance = _meander(rng, rows, columns, knobs["bend_spacing"], 0.22, step)
    distance = distance + 0.05 * (_noise(rng, rows, columns, 0.3, step) - 0.5)  # ragged walls
    water, floor, wall, steps = knobs["river"], knobs["floor"], knobs["wall"], knobs["steps"]
    t = np.clip((distance - floor) / wall, 0.0, 1.0) * steps
    stairs = (np.floor(t) + smoothstep(0.7, 1.0, t - np.floor(t))) / steps  # flat ledges, steep risers
    heights = np.where(distance < floor, 0.01, plateau * np.minimum(stairs, 1.0))
    heights = np.where(distance < water, -0.004 - 0.025 * (1 - distance / water), heights)
    marks = np.where((distance >= water) & (distance < floor), 0.5, 0.0)
    return Shape(heights, marks)


def pack_ice(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Floes of sea ice split by dark leads of open water, and a few icebergs. Marks: 1 on the icebergs."""
    value = 0.7 * _noise(rng, rows, columns, knobs["floe_size"], step) + 0.3 * _noise(rng, rows, columns, 0.2, step)
    sea = _level_for_share(value, knobs["open_water"])
    leads = 1 - np.abs(2 * _noise(rng, rows, columns, 0.35, step) - 1)  # a network of cracks where this is high
    floe = smoothstep(sea, sea + 0.04, value) * smoothstep(0.96, 0.9, leads)
    heights = np.where(floe > 0.2, 0.014 * floe - 0.002, -0.004 - np.maximum(sea - value, 0.0) * 0.5)
    berg_level = _level_for_share(value, knobs["berg_share"])
    peak = float(np.max(value))
    berg = np.clip((value - berg_level) / max(peak - berg_level, 1e-9), 0.0, 1.0)
    heights = np.where(berg > 0, 0.03 + np.sqrt(berg) * 0.8 * max_height, heights)
    return Shape(heights, (berg > 0).astype(np.float64))


def volcano(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Black volcanic hills with lakes (below `lava_level`, 0 to 1 of the noise) and rivers of lava (below 0) in the
    low ground.
    """
    value = _normalized(eroded_noise(rng, rows, columns, knobs["size"] / step, octaves=6))
    level = knobs["lava_level"]
    heights = np.where(
        value > level, (np.maximum(value - level, 0.0) / (1 - level)) ** 1.4 * max_height, (value - level) * 0.2
    )
    # Rivers: channels carved along a line of the noise, with sloping banks (not a wall a grid point wide).
    channel = smoothstep(0.04, 0.015, np.abs(_noise(rng, rows, columns, knobs["river_size"], step) - 0.5))
    return Shape(heights * (1 - channel) - 0.008 * channel)


def swamp(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """Murky water full of low muddy islets with reeds (and dead trees, see `dead_trees`). Marks: reeds."""
    value = 0.7 * _noise(rng, rows, columns, knobs["size"], step)
    value += 0.3 * _noise(rng, rows, columns, knobs["detail_size"], step)
    sea = _level_for_share(value, knobs["water_share"])
    heights = np.where(value > sea, 0.003 + (value - sea) * 0.12, (value - sea) * 0.3)
    reeds = smoothstep(sea + 0.03, sea + 0.07, value) * smoothstep(0.45, 0.6, _noise(rng, rows, columns, 0.12, step))
    return Shape(heights, reeds)


def clouds(rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
    """A deck of low clouds (`cover`: the share it covers); through the gaps (below 0), the dark ground far below."""
    value = 0.7 * _noise(rng, rows, columns, knobs["size"], step) + 0.3 * _noise(rng, rows, columns, 0.28, step)
    cover = _level_for_share(value, knobs["cover"])
    peak = float(np.max(value))
    rise = np.clip((value - cover) / max(peak - cover, 1e-9), 0.0, 1.0)
    puffs = rise**0.4 * smoothstep(0.0, 0.12, rise) * max_height  # round puffs, their edges rounded off too
    return Shape(np.where(value > cover, puffs, -0.002 - (cover - value) * 0.3))


def _scatter(
    rng: random.Random, where: NDArray[np.bool_], chance: float, step_x: float, step_y: float
) -> list[tuple[float, float]]:
    """Places (x, y) on some of the grid points where `where` is true, each with `chance`."""
    rows, columns = np.nonzero(where)
    return [
        (column * step_x + rng.uniform(-0.4, 0.4) * step_x, row * step_y + rng.uniform(-0.4, 0.4) * step_y)
        for row, column in zip(rows.tolist(), columns.tolist(), strict=True)
        if rng.random() < chance
    ]


def _inside(y: float, size: float, rows: int, step_y: float) -> bool:
    """Doesn't cross the end of the loop."""
    return size <= y <= rows * step_y - size


def palms(rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
    """Palms on the grass around the desert's oases (on a share `chance` of its points)."""
    marks = shape.marks if shape.marks is not None else np.zeros_like(shape.heights)
    rows = shape.heights.shape[0]
    size = knobs["size"]
    return [
        Prop("palm", x, y, size, size, rng.uniform(*knobs["height"]), rng.randrange(1 << 30))
        for x, y in _scatter(rng, np.abs(marks - 0.5) < 0.1, knobs["chance"], step_x, step_y)
        if _inside(y, 0.02, rows, step_y)
    ]


def dead_trees(rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
    """A few dead trees on the swamp's islets (on a share `chance` of their points)."""
    rows = shape.heights.shape[0]
    size = knobs["size"]
    return [
        Prop("dead_tree", x, y, size, size, rng.uniform(*knobs["height"]), rng.randrange(1 << 30))
        for x, y in _scatter(rng, shape.heights > 0.006, knobs["chance"], step_x, step_y)
        if _inside(y, 0.02, rows, step_y)
    ]


LANDSCAPES: dict[str, Landscape] = {
    "mountains": mountains,
    "rolling": rolling,
    "level_ground": level_ground,
    "hills": hills,
    "islands": islands,
    "desert": desert,
    "forest": forest,
    "canyon": canyon,
    "pack_ice": pack_ice,
    "volcano": volcano,
    "swamp": swamp,
    "clouds": clouds,
}
# The numbers each landscape needs (ground.shape in the scenery).
KNOBS: dict[str, tuple[str, ...]] = {
    "mountains": ("range_size", "crest_size"),
    "rolling": ("height", "swell_size", "detail_size"),
    "level_ground": ("height", "size"),
    "hills": ("size", "crater_spacing", "crater_radius"),
    "islands": ("land_share", "size", "detail_size", "fine_size"),
    "desert": ("dune_spacing", "mesa_size", "pool_size"),
    "forest": ("canopy_size", "river_spacing", "river_width"),
    "canyon": ("bend_spacing", "river", "floor", "wall", "steps"),
    "pack_ice": ("open_water", "berg_share", "floe_size"),
    "volcano": ("size", "lava_level", "river_size"),
    "swamp": ("water_share", "size", "detail_size"),
    "clouds": ("cover", "size"),
}
FLORAS: dict[str, Flora] = {"palms": palms, "dead_trees": dead_trees}
FLORA_KNOBS: dict[str, tuple[str, ...]] = {
    "palms": ("chance", "size", "height"),
    "dead_trees": ("chance", "size", "height"),
}
