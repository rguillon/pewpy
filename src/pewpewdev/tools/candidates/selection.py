"""Making ships, and keeping the most different ones."""

import math
import random
from collections.abc import Callable
from typing import TypeVar

from pewpewdev.tools.candidates.aircraft import (
    Parts,
    aircraft,
    aircraft_layers,
)
from pewpewdev.tools.candidates.canvas import Rng
from pewpewdev.tools.candidates.details import (
    detail,
    trim,
)
from pewpewdev.tools.candidates.industrial import industrial, industrial_shaping
from pewpewdev.tools.candidates.layers import layered_drawing
from pewpewdev.tools.candidates.palette import palette
from pewpewdev.tools.candidates.shaping import engines_at_height, sculpt

# Shares of each group, by --kind.
MIXES = {
    "all": {"aircraft": 0.45, "symmetric": 0.32, "lopsided": 0.23},
    "aircraft": {"aircraft": 1.0},
    "industrial": {"symmetric": 0.6, "lopsided": 0.4},
}
T = TypeVar("T")


def features(rows: list[str], symmetric: bool) -> list[float]:
    """For telling ships apart: the outline shrunk to 8 x 8, the size, the proportions, symmetry, how full."""
    height, width = len(rows), len(rows[0])
    grid = []
    for gy in range(8):
        for gx in range(8):
            y0, x0 = gy * height // 8, gx * width // 8
            y1, x1 = max(y0 + 1, (gy + 1) * height // 8), max(x0 + 1, (gx + 1) * width // 8)
            cells = [rows[y][x] != "." for y in range(y0, y1) for x in range(x0, x1)]
            grid.append(sum(cells) / len(cells))
    filled = sum(char != "." for row in rows for char in row) / (width * height)
    return [*grid, 3 * width / 35, 3 * height / 35, 2 * math.log(width / height), 0.4 * (not symmetric), 2 * filled]


def ship(rng: Rng, group: str) -> tuple[list[float], Callable[[], dict]] | None:
    """One ship of a group ("aircraft", "symmetric" or "lopsided"): its features, and what makes its drawing (only
    the ships kept are built in 3D).
    """
    parts: Parts | None = None
    if group == "aircraft":
        cv, symmetric, parts = aircraft(rng)
    else:
        cv, symmetric = industrial(rng, group == "lopsided")
    trim(cv, symmetric, parts)
    if cv.w < 5 or cv.h < 5:
        return None
    engines = detail(rng, cv, symmetric)
    rows = cv.rows()
    colors = palette(rng, {char for row in rows for char in row} | {"D", "h"})  # underside, under raised cells

    def make() -> dict:
        if parts is not None:
            return {**layered_drawing(aircraft_layers(cv, parts), cv, colors), "engines": engines}
        cells, heights = sculpt(cv, industrial_shaping(cv))
        return {**layered_drawing(cells, cv, colors), "engines": engines_at_height(engines, heights)}

    return features(rows, symmetric), make


def most_different(pool: list[tuple[list[float], T]], count: int) -> list[T]:
    """`count` things of the pool, by their features: each next one is the farthest from all those already kept."""
    kept = [0]
    distance = [math.dist(f, pool[0][0]) for f, _ in pool]
    while len(kept) < min(count, len(pool)):
        index = max(range(len(pool)), key=distance.__getitem__)
        kept.append(index)
        distance = [min(d, math.dist(f, pool[index][0])) for d, (f, _) in zip(distance, pool, strict=True)]
    return [pool[index][1] for index in kept]


def generate(count: int, kind: str, seed: int, pool_factor: int) -> list[dict]:
    rng = random.Random(seed)  # noqa: S311 - drawings, not cryptography
    drawings = []
    shares = MIXES[kind]
    for index, (group, share) in enumerate(shares.items()):
        wanted = count - len(drawings) if index == len(shares) - 1 else round(count * share)
        pool = [made for _ in range(wanted * pool_factor) if (made := ship(rng, group)) is not None]
        if pool:
            drawings += [make() for make in most_different(pool, wanted)]
    rng.shuffle(drawings)
    return drawings
