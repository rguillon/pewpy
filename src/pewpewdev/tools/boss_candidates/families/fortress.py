"""The fortress family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def fortress(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A square keep with round towers at its corners."""
    tower = max(3.0, half * 0.25)
    cv.rect(mx - half + tower, mx + half - tower, top + tower, bottom - tower, "h")
    for y in (top + tower, bottom - tower):
        cv.ellipse(mx - half + tower, y, tower, tower, "N")
        cv.ellipse(mx + half - tower, y, tower, tower, "N")
    cv.rect(mx - half + tower, mx + half - tower, top + tower + 3, top + tower + 4, "k")
