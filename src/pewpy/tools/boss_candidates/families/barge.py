"""The barge family."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def barge(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a long hull with rows of cargo containers and a small bridge tower at the back."""
    cv.rect(mx - half, mx + half, top + 3, bottom - 2, "h")
    cv.polygon([(mx - half, bottom - 2), (mx + half, bottom - 2), (mx, bottom)], "h")
    size = rng.randint(3, 5)
    for y in range(round(top) + 8, round(bottom) - 4, size + 1):
        for x in range(round(mx - half + 1), round(mx), size + 1):
            if rng.random() < 0.85:
                cv.rect(x, x + size - 1, y, y + size - 1, "T" if (x + y) % 2 else "S", "both")
    cv.rect(mx - 3, mx + 3, top, top + 6, "S")
