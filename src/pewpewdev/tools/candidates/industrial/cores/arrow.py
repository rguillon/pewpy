"""The arrow core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_arrow(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    """Draw an arrowhead with a notched back."""
    notch = rng.uniform(0.2, 0.4) * cv.h
    cv.polygon([(mx - half, 0), (mx, notch), (mx + half, 0), (mx + 0.8, cv.h - 0.5), (mx - 0.8, cv.h - 0.5)], "h")
