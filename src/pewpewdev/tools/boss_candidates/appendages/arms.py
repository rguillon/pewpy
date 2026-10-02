"""The arms appendage."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def arms(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    """Draw arms reaching out from the core, each ending in a pod."""
    y = rng.uniform(0.3, 0.7) * cv.h
    end = rng.uniform(2, max(2.5, mx - half - 2))
    cv.rect(end, mx - half * 0.5, y, y + 2, "N", side)
    cv.ellipse(end, y + 1, 3, 4, "h")
    if side == "both":
        cv.ellipse(cv.mirror(end), y + 1, 3, 4, "h")
