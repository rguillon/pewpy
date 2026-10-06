"""A little geometry for drawing shapes: points, and whether one is inside a polygon."""

import random

Point = tuple[float, float]
Rng = random.Random


def inside(x: float, y: float, points: list[Point]) -> bool:
    """Tell whether a point is inside a polygon (even-odd rule)."""
    inside = False
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1], strict=True):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside
