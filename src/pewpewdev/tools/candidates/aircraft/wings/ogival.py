"""An ogival wing."""

from pewpewdev.tools.candidates.canvas import Point, Rng


def ogival(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
    """A delta whose leading edge curves out from the nose to the tip."""
    back = front - height * rng.uniform(0.5, 0.7)
    points = [(root_x, front + 1)]
    for i in range(1, 8):
        t = i / 7
        points.append((root_x - (root_x + 0.5) * t**0.6, front + 1 - (front - back - 1) * t**1.8))
    return [*points, (-0.5, back), (root_x, back)]
