"""A delta wing."""

from pewpewdev.tools.candidates.canvas import Point, Rng


def delta(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
    """Plan a delta wing: a triangle from the root to a blunt tip at the back."""
    back = front - height * rng.uniform(0.5, 0.7)
    return [(root_x, front), (-0.5, back + 1.2), (-0.5, back), (root_x, back)]
