"""The modular family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def modular(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Blocks of different sizes on a lattice of trusses."""
    cv.rect(mx - 1, mx + 1, top, bottom, "N")
    for y in range(round(top) + 2, round(bottom) - 3, rng.randint(6, 9)):
        cv.rect(mx - half + 2, mx, y, y + 1, "k", "both")
        for _ in range(rng.randint(1, 2)):
            width, height = rng.uniform(3, max(3.0, half / 2)), rng.randint(3, 6)
            left = mx - rng.uniform(width + 1, max(width + 1.5, half))
            cv.rect(left, left + width, y - height // 2, y + height // 2, "h", "both")
    cv.ellipse(mx, bottom - 5, 3, 4, "h")
