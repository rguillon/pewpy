"""The wedge core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_wedge(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # narrow at the back, wide at the front
    cv.polygon([(mx - 1, 0), (mx + 1, 0), (mx + half, cv.h * 0.8), (mx, cv.h - 0.5), (mx - half, cv.h * 0.8)], "h")
