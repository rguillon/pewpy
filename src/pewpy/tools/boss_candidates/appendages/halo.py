"""The halo appendage."""

import math

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def halo(rng: Rng, cv: Canvas, mx: float, _half: float, _side: str) -> None:
    """Draw a halo: a ring around the core."""
    my = cv.h * rng.uniform(0.35, 0.6)
    r = min(cv.w / 2 - 1, cv.h / 2 - 1) * rng.uniform(0.8, 1.0)
    for a in range(0, 360, 2):
        x, y = mx + r * math.cos(math.radians(a)), my + r * 0.7 * math.sin(math.radians(a))
        cv.set(round(x), round(y), "N" if cv.get(round(x), round(y)) == "." else cv.get(round(x), round(y)))
