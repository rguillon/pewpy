"""The crescent family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def crescent(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw an arc, its horns reaching forward."""
    length = bottom - top
    cv.ellipse(mx, top + length * 0.4, half, length * 0.4, "h")
    cv.ellipse(mx, top + length * 0.85, half * rng.uniform(0.5, 0.65), length * 0.5, ".")
    cv.ellipse(mx, top + length * 0.3, half * 0.25, length * 0.3, "T")
