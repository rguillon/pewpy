"""The crescent core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_crescent(_rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    """Draw a crescent, its horns reaching forward."""
    cv.ellipse(mx, cv.h * 0.35, half + 0.4, cv.h * 0.35, "h")
    cv.ellipse(mx, cv.h * 0.75, half * 0.55, cv.h * 0.45, ".")
    cv.rect(mx - 1, mx + 1, 0, cv.h * 0.5, "h")
