"""A little geometry: points, whether one is inside a polygon, and how far sizes are from those wanted."""

import math
import random

Point = tuple[float, float]
Rng = random.Random


def miss(have: tuple[float, ...], want: tuple[float, ...]) -> float:
    """Tell how far sizes are from those wanted: 0 when they're the same, more the farther (bigger or smaller)."""
    return sum(abs(math.log(max(0.5, a) / max(0.5, b))) for a, b in zip(have, want, strict=True))


def inside(x: float, y: float, points: list[Point]) -> bool:
    """Tell whether a point is inside a polygon (even-odd rule)."""
    inside = False
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1], strict=True):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside
