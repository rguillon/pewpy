"""The mandible attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def mandible(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x = max(0, edge - rng.randint(0, 2))
    start = rng.uniform(0.4, 0.65) * cv.h
    cv.polygon(
        [(x - 1, start), (x + 1.5, start), (x + rng.uniform(1, 3), cv.h - 0.5), (x - 0.5, cv.h - 1.5)], "N", side
    )
