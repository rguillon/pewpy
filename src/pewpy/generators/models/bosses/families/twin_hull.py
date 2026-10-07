"""The twin hull family."""

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.common.geometry import Rng


def twin_hull(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Two big hulls side by side, joined by bridges, a pod between them."""
    width, cut = half * rng.uniform(0.35, 0.5), max(2.0, half * 0.12)
    for left in (mx - half, mx + half - width):
        cv.polygon([(left, top + cut), (left + cut, top), (left + width - cut, top), (left + width, top + cut),
                    (left + width, bottom), (left, bottom)], "h")  # fmt: skip
    for _ in range(rng.randint(2, 4)):
        y = top + rng.uniform(0.15, 0.8) * (bottom - top)
        cv.rect(mx - half + width, mx + half - width, y, y + rng.randint(2, 4), "T")
    cv.ellipse(mx, (top + bottom) / 2, half * 0.2, (bottom - top) * 0.2, "h")
