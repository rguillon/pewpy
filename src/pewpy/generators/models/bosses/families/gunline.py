"""The gunline family."""

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.common.geometry import Rng


def gunline(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Several long tubes side by side, held by cross beams: a battery of guns."""
    tubes = rng.choice((3, 5))
    spacing = 2 * half / (tubes - 1)
    for i in range(tubes):
        x = mx - half + i * spacing
        cv.rect(x - 1.5, x + 1.5, top + (0 if i % 2 else 4), bottom - (0 if i == tubes // 2 else 4), "h")
    for y in (top + (bottom - top) * 0.3, top + (bottom - top) * 0.6):
        cv.rect(mx - half, mx + half, y, y + 2, "T")
