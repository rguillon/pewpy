"""The cannon attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def cannon(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    """Draw a big gun along the flank."""
    x = rng.randint(max(0, edge - 2), max(0, edge))
    cv.rect(x - 1, x + 1, rng.uniform(0.1, 0.4) * cv.h, cv.h * 0.75, "t", side)
    cv.line(x, cv.h * 0.75, x, cv.h - 1, "r", side)
