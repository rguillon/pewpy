"""The smooth grounds' landscapes (relief.py): the shape of each kind of ground, as heights and marks.

Every generator takes (rng, rows, columns, highest point, step) and returns a Shape, looping along the rows. Sizes
below are in world units (divided by the step to count grid points). Grounds with water, lava or the gaps of a
cloud deck have them below height 0 (see relief.py); the marks are for the ground shader (ground_shader.py), their
meaning depends on the landscape. A few landscapes also have sparse props, placed from their shape ("flora").

Numpy only, independent from Panda3D.
"""

import math
import random
from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from pewpy.scenery.relief import FloatGrid, Shape, eroded_noise, periodic_noise, ridged_mountains, smoothstep
from pewpy.scenery.settlement import Prop

Generator = np.random.Generator
# (rng, shape, step across, step down) -> props standing on the ground
Flora = Callable[[random.Random, Shape, float, float], list[Prop]]


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
    whole number of bends per loop."""
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


def mountains(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Eroded ranges with sharp crests, flat valley floors between them."""
    ranges = eroded_noise(rng, rows, columns, 1.1 / step)
    crests = ridged_mountains(rng, rows, columns, 0.6 / step, octaves=5)
    middle, top = np.percentile(ranges, 40), np.percentile(ranges, 90)
    value = ranges + 0.6 * crests * smoothstep(middle, top, ranges)  # sharp crests on the high ground only
    value = _normalized(value, 3, 99.7)  # the lowest 3 % flat: valley floors
    return Shape(max_height * value**1.4)


def rolling(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Gently rolling ground for farmland: wide low swells (`max_height` is for what stands on it, not used)."""
    return Shape(0.035 * (0.7 * _noise(rng, rows, columns, 1.4, step) + 0.3 * _noise(rng, rows, columns, 0.5, step)))


def level_ground(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Nearly flat ground for the city and the refinery, just not perfectly even."""
    return Shape(0.006 * _noise(rng, rows, columns, 0.8, step))


def hills(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """A dusty planet: low eroded hills pocked with craters. Marks: the craters' rims and the dust thrown out."""
    value = _normalized(eroded_noise(rng, rows, columns, 0.9 / step, octaves=6))
    rims = np.zeros_like(value)
    for _ in range(max(1, round(rows * step / 0.5))):
        radius = rng.uniform(0.07, 0.18)
        distance = _wrapped_distance(rows, columns, step, rng.uniform(0, columns * step), rng.uniform(0, rows * step))
        d = distance / radius
        value -= 0.55 * np.clip(1 - d * d, 0.0, 1.0)  # the bowl
        rim = np.exp(-(((d - 1.05) / 0.18) ** 2))
        value += 0.22 * rim
        rims = np.maximum(rims, rim + 0.4 * np.exp(-d) * (d > 1))
    return Shape(max_height * np.clip(value, 0.0, 1.0), np.clip(rims, 0.0, 1.0))


def islands(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Islands in a sea (22 % land), shelving into shallows around them."""
    value = 0.65 * _noise(rng, rows, columns, 0.7, step) + 0.25 * _noise(rng, rows, columns, 0.28, step)
    value += 0.1 * _noise(rng, rows, columns, 0.1, step)
    sea = _level_for_share(value, 0.22)
    peak = float(np.max(value))
    land = np.clip((value - sea) / max(peak - sea, 1e-9), 0.0, 1.0) ** 0.8 * max_height
    return Shape(np.where(value > sea, land, (value - sea) * 0.7))


def desert(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Long dune ridges, flat-topped rock mesas, a few oasis pools ringed with grass (and palms, see `palms`).
    Marks: 0 sand, 0.5 the grass around the pools, 1 rock."""
    crests = max(1, round(rows * step / 0.5))  # dune ridges per loop: a whole number, so they loop too
    y = np.arange(rows)[:, None] / rows
    x = np.arange(columns)[None, :] * step
    phase = 2 * math.pi * crests * y + 1.4 * x + 4 * _noise(rng, rows, columns, 0.7, step)
    dune = (0.5 + 0.5 * np.sin(phase + 0.6 * np.sin(phase))) ** 2  # a gentle windward side, a steep slip face
    heights = 0.012 + dune * 0.3 * max_height
    mesas = _noise(rng, rows, columns, 1.05, step)
    rock = smoothstep(0.74, 0.77, mesas)  # edges a few grid points wide: no jagged cliffs
    heights = np.maximum(heights, 0.6 * max_height * rock)  # a ledge around each mesa...
    heights = np.maximum(heights, max_height * smoothstep(0.79, 0.83, mesas))  # ...and its flat top
    pools = _noise(rng, rows, columns, 0.56, step)
    grass = (pools >= 0.14) & (pools < 0.19) & (rock < 0.5)  # a ring around the pool
    heights = np.where(grass, np.minimum(heights, 0.008), heights)
    heights = np.where((pools < 0.14) & (rock < 0.5), (pools - 0.14) * 0.6, heights)
    marks = np.where(rock > 0.5, 1.0, np.where(grass, 0.5, 0.0))
    return Shape(heights, marks)


def forest(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """A canopy over rolling ground, some clearings, and a river winding through. Marks: 1 under the canopy."""
    ground = 0.04 * _noise(rng, rows, columns, 1.2, step)
    canopy = smoothstep(0.66, 0.6, _noise(rng, rows, columns, 0.84, step))  # clearings where the noise is high
    river = _meander(rng, rows, columns, 2.8, 0.3, step)
    half_width = 0.06
    canopy *= smoothstep(half_width * 1.4, half_width * 2.2, river)  # open banks
    heights = ground + 0.045 * canopy
    heights = np.where(river < half_width, -0.005 - 0.03 * (1 - river / half_width), heights)
    return Shape(heights, canopy)


def canyon(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """A plateau cut by a winding canyon: stepped cliffs, sandbanks, a river at the bottom. Marks: 0.5 sand."""
    plateau = max_height * (0.85 + 0.15 * _noise(rng, rows, columns, 0.7, step))
    distance = _meander(rng, rows, columns, 3.1, 0.22, step)
    distance = distance + 0.05 * (_noise(rng, rows, columns, 0.3, step) - 0.5)  # ragged walls
    water, floor, wall, steps = 0.11, 0.22, 0.45, 4
    t = np.clip((distance - floor) / wall, 0.0, 1.0) * steps
    stairs = (np.floor(t) + smoothstep(0.7, 1.0, t - np.floor(t))) / steps  # flat ledges, steep risers
    heights = np.where(distance < floor, 0.01, plateau * np.minimum(stairs, 1.0))
    heights = np.where(distance < water, -0.004 - 0.025 * (1 - distance / water), heights)
    marks = np.where((distance >= water) & (distance < floor), 0.5, 0.0)
    return Shape(heights, marks)


def pack_ice(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Floes of sea ice split by dark leads of open water, and a few icebergs. Marks: 1 on the icebergs."""
    value = 0.7 * _noise(rng, rows, columns, 0.5, step) + 0.3 * _noise(rng, rows, columns, 0.2, step)
    sea = _level_for_share(value, 0.6)
    leads = 1 - np.abs(2 * _noise(rng, rows, columns, 0.35, step) - 1)  # a network of cracks where this is high
    floe = smoothstep(sea, sea + 0.04, value) * smoothstep(0.96, 0.9, leads)
    heights = np.where(floe > 0.2, 0.014 * floe - 0.002, -0.004 - np.maximum(sea - value, 0.0) * 0.5)
    berg_level = _level_for_share(value, 0.03)
    peak = float(np.max(value))
    berg = np.clip((value - berg_level) / max(peak - berg_level, 1e-9), 0.0, 1.0)
    heights = np.where(berg > 0, 0.03 + np.sqrt(berg) * 0.8 * max_height, heights)
    return Shape(heights, (berg > 0).astype(np.float64))


def volcano(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Black volcanic hills with lakes and rivers of lava (below 0) in the low ground."""
    value = _normalized(eroded_noise(rng, rows, columns, 0.77 / step, octaves=6))
    heights = np.where(value > 0.25, (np.maximum(value - 0.25, 0.0) / 0.75) ** 1.4 * max_height, (value - 0.25) * 0.2)
    # Rivers: channels carved along a line of the noise, with sloping banks (not a wall a grid point wide).
    channel = smoothstep(0.04, 0.015, np.abs(_noise(rng, rows, columns, 0.63, step) - 0.5))
    return Shape(heights * (1 - channel) - 0.008 * channel)


def swamp(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """Murky water full of low muddy islets with reeds (and dead trees, see `dead_trees`). Marks: reeds."""
    value = 0.7 * _noise(rng, rows, columns, 0.42, step) + 0.3 * _noise(rng, rows, columns, 0.175, step)
    sea = _level_for_share(value, 0.45)
    heights = np.where(value > sea, 0.003 + (value - sea) * 0.12, (value - sea) * 0.3)
    reeds = smoothstep(sea + 0.03, sea + 0.07, value) * smoothstep(0.45, 0.6, _noise(rng, rows, columns, 0.12, step))
    return Shape(heights, reeds)


def clouds(rng: Generator, rows: int, columns: int, max_height: float, step: float) -> Shape:
    """A deck of low clouds (60 % cover); through the gaps (below 0), the dark ground far below."""
    value = 0.7 * _noise(rng, rows, columns, 0.9, step) + 0.3 * _noise(rng, rows, columns, 0.28, step)
    cover = _level_for_share(value, 0.6)
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


def palms(rng: random.Random, shape: Shape, step_x: float, step_y: float) -> list[Prop]:
    """Palms on the grass around the desert's oases."""
    marks = shape.marks if shape.marks is not None else np.zeros_like(shape.heights)
    rows = shape.heights.shape[0]
    return [
        Prop("palm", x, y, 0.035, 0.035, rng.uniform(0.03, 0.045), rng.randrange(1 << 30))
        for x, y in _scatter(rng, np.abs(marks - 0.5) < 0.1, 0.3, step_x, step_y)
        if _inside(y, 0.02, rows, step_y)
    ]


def dead_trees(rng: random.Random, shape: Shape, step_x: float, step_y: float) -> list[Prop]:
    """A few dead trees on the swamp's islets."""
    rows = shape.heights.shape[0]
    return [
        Prop("dead_tree", x, y, 0.03, 0.03, rng.uniform(0.04, 0.07), rng.randrange(1 << 30))
        for x, y in _scatter(rng, shape.heights > 0.006, 0.01, step_x, step_y)
        if _inside(y, 0.02, rows, step_y)
    ]
