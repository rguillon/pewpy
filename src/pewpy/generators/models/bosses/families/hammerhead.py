"""The hammerhead family."""

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.common.geometry import Rng


def hammerhead(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a long body with a wide armored bar across its front."""
    body, head = half * rng.uniform(0.25, 0.4), (bottom - top) * rng.uniform(0.12, 0.2)
    cv.rect(mx - body, mx + body, top, bottom, "h")
    cv.rect(mx - half, mx + half, bottom - head - 2, bottom - 2, "N")
    length = bottom - top
    cv.polygon([(mx - body, top + length * 0.2), (mx - half, top + length * 0.35),
                (mx - half, top + length * 0.45), (mx - body, top + length * 0.45)], "w", "both")  # fmt: skip
