"""The flying wing family."""

from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.common.geometry import Rng


def flying_wing(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a huge delta with a blended body."""
    length = bottom - top
    back = top + rng.uniform(0.0, 0.2) * length
    cv.polygon([(mx - half, back + length * 0.2), (mx, top), (mx + half, back + length * 0.2),
                (mx + half, back + length * 0.35), (mx, bottom), (mx - half, back + length * 0.35)], "w")  # fmt: skip
    cv.ellipse(mx, top + length * 0.45, half * 0.28, length * 0.42, "h")
