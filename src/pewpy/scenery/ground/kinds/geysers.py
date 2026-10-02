"""A geyser basin: a pale crust of sinter with hot pools ringed in colored mats, terraced mounds, wooded ridges."""

import math
import random

import numpy as np

from pewpy.scenery.ground.landscapes import Flora, Generator, Landscape, inside, noise, scatter
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import Knobs

PLAIN = 0.004  # world units: the crust's lowest, just above the water
MAT = 0.5  # the marks: the mats up to this (at the water's edge)...
MOUND_SINTER = 0.75  # ...the terraced mounds from this (dry) to 1 (water on their ledges)


class Geysers(Landscape):
    """A geyser basin: hot pools, terraced mounds, wooded ridges."""

    knobs = ("spring_spacing", "spring_radius", "mat_width", "mound_spacing", "mound_radius", "steps", "ridge_share")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape a flat crust of sinter cut by hot pools, with terraced mounds on it and wooded ridges around.

        Pools (about `spring_spacing` apart, `spring_radius` wide) are below 0, ringed by mats reaching `mat_width`
        of their radius out, in fingers where the hot water runs off. Mounds (`mound_spacing`, `mound_radius`) step
        up in `steps` terraces, each ledge a shallow pool behind a rim. Ridges cover `ridge_share` of the ground.
        Marks: the mats up to 0.5 (at the water's edge), MOUND_SINTER the terraces, 1 the water on their ledges.
        """
        heights = PLAIN + 0.02 * noise(rng, rows, columns, 1.1, step)
        ridges = noise(rng, rows, columns, 1.6, step) + 0.25 * noise(rng, rows, columns, 0.45, step)
        level = float(np.percentile(ridges, 100 * (1 - knobs["ridge_share"])))
        ridge = smoothstep(level, level + 0.3, ridges)
        lumps = 0.6 * noise(rng, rows, columns, 0.3, step) + 0.4 * noise(rng, rows, columns, 0.1, step)
        heights = heights + max_height * ridge**1.2 * (0.4 + 0.6 * lumps)
        free = ridges < level - 0.03  # where springs and mounds can go
        ragged = noise(rng, rows, columns, 0.12, step)
        runoff = noise(rng, rows, columns, 0.18, step)
        marks = np.zeros_like(heights)
        width, height = columns * step, rows * step
        steps = knobs["steps"]
        for x, y in _spread(rng, free, step, knobs["mound_spacing"], width, height):
            dx, dy = _offsets(rows, columns, step, x, y)
            d = np.hypot(dx, dy) / rng.uniform(*knobs["mound_radius"]) + 0.2 * (ragged - 0.5)
            t = np.clip(1 - d, 0.0, 1.0) * steps
            ledge, along = np.floor(t), t - np.floor(t)  # which terrace, and how far across it (0: its rim)
            rise = smoothstep(0.8, 1.0, along) + 0.15 * smoothstep(0.0, 0.08, along) * smoothstep(0.25, 0.1, along)
            top = rng.uniform(0.35, 0.5) * max_height
            mound = PLAIN + top * np.minimum(ledge + rise, steps) / steps
            heights = np.maximum(heights, mound)
            water = smoothstep(0.12, 0.22, along) * smoothstep(0.8, 0.7, along) * (ledge >= 1)
            water = np.where(ledge >= steps - 1, smoothstep(0.1, 0.3, along + ledge - (steps - 1)), water)  # the spring
            edge = smoothstep(-1.0, 0.6, (1 - d) * steps)  # through the mats' colors: an apron of runoff round the foot
            marks = np.maximum(marks, edge * (MOUND_SINTER + (1 - MOUND_SINTER) * water))
            free &= d > 1.3
        hot = free & (noise(rng, rows, columns, 0.9, step) > 0.5)  # the springs gather in a few hot patches
        for x, y in _spread(rng, hot, step, knobs["spring_spacing"], width, height):
            low, high = knobs["spring_radius"]
            radius = low + (high - low) * rng.random() ** 2  # many small ones, a few big ones
            dx, dy = _offsets(rows, columns, step, x, y)
            d = np.hypot(dx, dy) / radius + 0.4 * (ragged - 0.5)
            # The mats: a ring round the pool, and a fan of fingers down the way its water runs off.
            way = rng.uniform(0, 2 * math.pi)
            towards = np.maximum((dx * math.cos(way) + dy * math.sin(way)) / np.maximum(np.hypot(dx, dy), 1e-9), 0)
            reach = 1 + knobs["mat_width"] * (0.25 + 2.5 * towards**2 * (0.3 + runoff))
            marks = np.maximum(marks, MAT * smoothstep(reach, 1.0, d))
            pool = -0.002 - 0.03 * np.clip(1 - d, 0.0, 1.0) ** 0.6  # shelving to a deep middle
            heights = np.where(d < 1, np.minimum(heights, pool), heights)
        return Shape(heights, marks)


def _offsets(rows: int, columns: int, step: float, x: float, y: float) -> tuple[np.ndarray, np.ndarray]:
    """How far every point is from (x, y), across and down (the rows looping: the shorter way)."""
    loop = rows * step
    dy = (np.arange(rows) * step - y + loop / 2) % loop - loop / 2
    dx = np.arange(columns) * step - x
    return np.broadcast_to(dx[None, :], (rows, columns)), np.broadcast_to(dy[:, None], (rows, columns))


def _spread(
    rng: Generator, free: np.ndarray, step: float, spacing: float, width: float, height: float
) -> list[tuple[float, float]]:
    """About one place per `spacing` squared, on free points, not too close to each other (the rows looping)."""
    rows, columns = free.shape
    chosen: list[tuple[float, float]] = []
    for _ in range(round(width * height / spacing**2) * 8):  # tries
        if len(chosen) >= round(width * height / spacing**2):
            break
        x, y = rng.uniform(0.1, width - 0.1), rng.uniform(0, height)
        if not free[int(y / step) % rows, min(int(x / step), columns - 1)]:
            continue
        if all(math.hypot(x - a, min(abs(y - b), height - abs(y - b))) > 0.6 * spacing for a, b in chosen):
            chosen.append((x, y))
    return chosen


class Snags(Flora):
    """Dead trees, bleached by the hot water, around the geyser basin's pools."""

    knobs = ("chance", "size", "height")

    def props(self, rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
        """Dead trees on the outer edge of the mats (on a share `chance` of their points)."""
        marks = shape.marks if shape.marks is not None else np.zeros_like(shape.heights)
        rows = shape.heights.shape[0]
        size = knobs["size"]
        return [
            Prop("dead_tree", x, y, size, size, rng.uniform(*knobs["height"]), rng.randrange(1 << 30))
            for x, y in scatter(rng, (marks > 0.02) & (marks < 0.15), knobs["chance"], step_x, step_y)
            if inside(y, 0.02, rows, step_y)
        ]
