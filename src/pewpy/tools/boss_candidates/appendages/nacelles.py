"""The nacelles appendage."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def nacelles(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    """Draw engine nacelles at the back, joined to the core by pylons."""
    x = rng.uniform(2, max(2.5, mx - half - 3))
    length = rng.uniform(0.3, 0.5) * cv.h
    cv.rect(x - 2, x + 2, 0, length, "h", side)
    cv.rect(x, mx - half * 0.5, length * 0.5, length * 0.5 + 2, "w", side)
