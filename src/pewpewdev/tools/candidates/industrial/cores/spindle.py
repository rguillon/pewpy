"""The spindle core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_spindle(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    cv.polygon([(mx - half, 0), (mx + half, 0), (mx + 0.6, cv.h - 0.5), (mx - 0.6, cv.h - 0.5)], "h")
