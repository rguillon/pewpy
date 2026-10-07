"""The citadel family."""

from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.common.geometry import Rng


def citadel(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Stacked tiers: a wide base at the front narrowing towards the back, like a fortress city."""
    tiers = rng.randint(3, 5)
    length = (bottom - top) / tiers
    for i in range(tiers):
        width = half * (0.35 + 0.65 * (i + 1) / tiers)
        cv.rect(mx - width, mx + width, top + i * length, top + (i + 1) * length - 1, "T" if i % 2 else "h")
        cv.rect(mx - width, mx - width + 1, top + i * length, top + (i + 1) * length - 1, "N", "both")
