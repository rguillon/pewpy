"""The boom attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def boom(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    """Draw a boom reaching back from the flank, an engine pod at its end."""
    x = rng.randint(0, max(0, edge - 2))
    cv.line(edge, rng.uniform(0.4, 0.8) * cv.h, x, rng.uniform(0, 0.25) * cv.h, "N", side)
    cv.rect(x - 1, x + 1, 0, rng.randint(2, 4), "h", side)  # an engine pod at its end
