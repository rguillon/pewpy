"""The trident family."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def trident(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a heavy body at the back with three prongs reaching forward."""
    length = bottom - top
    split = top + length * rng.uniform(0.35, 0.5)
    cv.rect(mx - half, mx + half, top, split, "h")
    width = max(2.0, half * 0.14)
    for x in (mx - half + width, mx):
        tip = bottom - (0 if x == mx else length * 0.1)
        cv.polygon([(x - width, split), (x + width, split), (x + 0.5, tip), (x - 0.5, tip)],
                   "N", "both" if x != mx else "one")  # fmt: skip
