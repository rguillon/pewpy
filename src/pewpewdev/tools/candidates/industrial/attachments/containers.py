"""The containers attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def containers(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    """Draw a column of cargo containers along the flank."""
    width = rng.randint(2, 3)
    x, y = max(0, edge - width), rng.uniform(0.05, 0.3) * cv.h
    while y < cv.h * 0.8:
        size = rng.randint(2, 4)
        cv.rect(x, x + width - 1, y, y + size - 1, "t", side)
        y += size + 1
