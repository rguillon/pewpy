"""The turret attachment."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def turret(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x, y = rng.randint(max(0, edge - 3), max(0, edge)), rng.uniform(0.2, 0.8) * cv.h
    cv.rect(x - 1, x + 1, y - 1, y + 1, "t", side)
    cv.line(x, y + 1, x, min(cv.h - 1, y + rng.randint(2, 5)), "r", side)  # its barrel
