"""The frame core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_frame(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # an open frame around a thin core
    cv.rect(mx - half, mx + half, 1, cv.h - 2, "N")
    cv.rect(mx - half + 2, mx + half - 2, 3, cv.h - 4, ".")
    cv.rect(mx - 1, mx + 1, 0, cv.h - 1, "h")
