"""The egg core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_egg(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    cv.ellipse(mx, cv.h / 2, half + 0.4, cv.h / 2 - 0.3, "h")
