"""The smooth grounds' landscapes (relief.py): what every landscape and flora is; each one is in grounds/.

A landscape makes the shape of a kind of ground, as heights and marks, looping along the rows. Its knobs are its own
numbers, from the level's scenery (see pewpy.scenery.params); sizes are in world units (divided by the step to count
grid points). Grounds with water have it below height 0 (see relief.py); the
marks are for the ground shader (shader/), their meaning depends on the landscape. A few landscapes also have sparse
props, placed from their shape: a flora. The helpers below are shared by the landscapes.

Numpy only, independent from Panda3D.
"""

import math
import random
from abc import ABC, abstractmethod
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray

from pewpy.scenery.ground.relief import FloatGrid, Shape, periodic_noise
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import Knobs

Generator = np.random.Generator


class Landscape(ABC):
    """The shape of a kind of ground."""

    knobs: ClassVar[tuple[str, ...]]  # the numbers it needs (ground.shape in the scenery)

    @abstractmethod
    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape the ground: `rows` x `columns` points `step` apart, at most `max_height` high (world units)."""


class Flora(ABC):
    """Sparse props standing on a landscape, placed from its shape."""

    knobs: ClassVar[tuple[str, ...]]  # the numbers it needs (flora.knobs in the scenery)

    @abstractmethod
    def props(self, rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
        """Place the props on `shape` (grid points `step_x` across and `step_y` down apart)."""


def noise(rng: Generator, rows: int, columns: int, size: float, step: float) -> FloatGrid:
    """Smooth noise, 0 to 1, about `size` world units from one bump to the next."""
    return periodic_noise(rng, rows, columns, size / step)


def normalized(values: FloatGrid, low: float = 1.0, high: float = 99.5) -> FloatGrid:
    """Stretched to 0-1 between two percentiles (clipped beyond)."""
    bottom, top = np.percentile(values, low), np.percentile(values, high)
    return np.clip((values - bottom) / max(top - bottom, 1e-9), 0.0, 1.0)


def level_for_share(values: FloatGrid, share: float) -> float:
    """Return the value above which `share` of the points lie."""
    return float(np.percentile(values, 100 * (1 - share)))


def meander(rng: Generator, rows: int, columns: int, spacing: float, swing: float, step: float) -> FloatGrid:
    """Return how far each point is from a river winding down the loop (world units).

    The river swings from side to side, a whole number of bends per loop.
    """
    bends = max(1, round(rows * step / spacing))
    phase = rng.uniform(0, 2 * math.pi)
    turn = 2 * math.pi * bends * np.arange(rows) / rows + phase
    middle = columns * step * (0.5 + swing * np.sin(turn) + 0.05 * np.sin(3 * turn))
    return np.abs(np.arange(columns)[None, :] * step - middle[:, None])


def scatter(
    rng: random.Random, where: NDArray[np.bool_], chance: float, step_x: float, step_y: float
) -> list[tuple[float, float]]:
    """Places (x, y) on some of the grid points where `where` is true, each with `chance`."""
    rows, columns = np.nonzero(where)
    return [
        (column * step_x + rng.uniform(-0.4, 0.4) * step_x, row * step_y + rng.uniform(-0.4, 0.4) * step_y)
        for row, column in zip(rows.tolist(), columns.tolist(), strict=True)
        if rng.random() < chance
    ]


def inside(y: float, size: float, rows: int, step_y: float) -> bool:
    """Doesn't cross the end of the loop."""
    return size <= y <= rows * step_y - size
