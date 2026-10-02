"""The antenna attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def antenna(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    """Draw an antenna sticking out of the flank."""
    cv.line(edge, rng.uniform(0.3, 0.7) * cv.h, max(0, edge - rng.randint(3, 7)), rng.uniform(0, cv.h), "r", side)
