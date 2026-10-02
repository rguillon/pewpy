"""A cranked wing."""

from pewpewdev.tools.candidates.canvas import Point, Rng


def cranked(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
    chord = height * rng.uniform(0.35, 0.5)
    crank_x = root_x - (root_x + 0.5) * rng.uniform(0.35, 0.5)
    crank_y = front - chord * 0.55
    tip_y = crank_y - (crank_x + 0.5) * rng.uniform(0.15, 0.45)
    return [
        (root_x, front),
        (crank_x, crank_y),
        (-0.5, tip_y),
        (-0.5, tip_y - max(1.0, chord * 0.12)),
        (root_x, front - chord),
    ]
