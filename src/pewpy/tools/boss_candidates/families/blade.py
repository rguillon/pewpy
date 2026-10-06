"""The blade family."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def blade(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a very long narrow wedge with fins along its sides."""
    width = half * rng.uniform(0.3, 0.45)
    cv.polygon([(mx - width, top), (mx + width, top), (mx, bottom)], "h")
    for i in range(rng.randint(2, 4)):
        y = top + (bottom - top) * (0.1 + 0.2 * i)
        cv.polygon([(mx - width * (1 - (y - top) / (bottom - top)), y), (mx - half, y + 2), (mx - half, y + 4),
                    (mx - width * (1 - (y + 5 - top) / (bottom - top)), y + 5)], "w", "both")  # fmt: skip
