"""The radiators appendage."""

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.common.geometry import Rng


def radiators(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    """Draw radiator panels: striped plates beside the core."""
    y, length = rng.uniform(0.1, 0.4) * cv.h, rng.randint(6, 14)
    left = rng.uniform(1, max(1.5, mx - half - 6))
    for i in range(length):
        cv.rect(left, mx - half * 0.6, y + i, y + i, "W" if i % 2 else "w", side)
