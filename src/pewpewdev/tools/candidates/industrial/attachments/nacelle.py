"""The nacelle attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def nacelle(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x = rng.randint(0, max(0, edge - 3))
    top, length = rng.uniform(0, 0.3) * cv.h, rng.uniform(0.35, 0.8) * cv.h
    width = rng.randint(1, 3)
    cv.rect(x, x + width, top, top + length, "N", side)
    cv.rect(x + width, edge, top + length * 0.4, top + length * 0.4 + 1, "w", side)  # its pylon
