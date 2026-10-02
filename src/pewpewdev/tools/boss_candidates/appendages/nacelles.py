"""The nacelles appendage."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def nacelles(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    x = rng.uniform(2, max(2.5, mx - half - 3))
    length = rng.uniform(0.3, 0.5) * cv.h
    cv.rect(x - 2, x + 2, 0, length, "h", side)
    cv.rect(x, mx - half * 0.5, length * 0.5, length * 0.5 + 2, "w", side)
