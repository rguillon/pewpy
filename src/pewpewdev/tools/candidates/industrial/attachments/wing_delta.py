"""The wing delta attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def wing_delta(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    root, tip = rng.uniform(0.15, 0.45) * cv.h, rng.uniform(0.6, 0.95) * cv.h
    cv.polygon([(edge + 0.5, root), (0, tip), (0, min(cv.h - 1, tip + 2)), (edge + 0.5, tip + 1)], "w", side)
