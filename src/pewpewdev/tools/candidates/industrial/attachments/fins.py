"""The fins attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def fins(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    """Draw a fin at the back."""
    tip = max(0, edge - rng.randint(2, 5))
    cv.polygon([(edge + 0.5, 1), (tip, -0.5), (tip, 1.5), (edge + 0.5, 4)], "w", side)
