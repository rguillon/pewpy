"""The fortress family."""

from pewpy.generators.models.bosses.canvas import Canvas
from pewpy.generators.models.common.geometry import Rng


def fortress(_rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a square keep with round towers at its corners."""
    tower = max(3.0, half * 0.25)
    cv.rect(mx - half + tower, mx + half - tower, top + tower, bottom - tower, "h")
    for y in (top + tower, bottom - tower):
        cv.ellipse(mx - half + tower, y, tower, tower, "N")
        cv.ellipse(mx + half - tower, y, tower, tower, "N")
    cv.rect(mx - half + tower, mx + half - tower, top + tower + 3, top + tower + 4, "k")
