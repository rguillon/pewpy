"""The diamond core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_diamond(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    """Draw a diamond."""
    middle = cv.h * rng.uniform(0.35, 0.6)
    cv.polygon([(mx, -0.5), (mx + half + 0.5, middle), (mx, cv.h - 0.5), (mx - half - 0.5, middle)], "h")
