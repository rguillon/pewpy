"""The radiator attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def radiator(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    y, length, width = rng.uniform(0.1, 0.5) * cv.h, rng.randint(3, 7), rng.randint(2, max(2, edge))
    for i in range(length):
        cv.rect(edge - width, edge, y + i, y + i, "W" if i % 2 else "w", side)
