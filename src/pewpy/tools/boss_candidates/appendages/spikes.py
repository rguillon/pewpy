"""The spikes appendage."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def spikes(rng: Rng, cv: Canvas, _mx: float, _half: float, side: str) -> None:
    """Draw armor spikes along the core's flanks."""
    for y in range(round(cv.h * 0.2), round(cv.h * 0.9), rng.randint(5, 8)):
        edge = next((x for x in range(cv.w) if cv.get(x, y) in "hHNT"), None)
        if edge is not None and edge > 3:
            cv.polygon([(edge + 0.5, y - 1), (edge - rng.uniform(3, 6), y + 1.5), (edge + 0.5, y + 2)], "N", side)
