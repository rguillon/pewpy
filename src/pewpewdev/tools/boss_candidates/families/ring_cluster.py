"""The ring cluster family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def ring_cluster(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Rings joined together around a spine."""
    count = rng.randint(2, 3)
    length = (bottom - top) / count
    for i in range(count):
        middle = top + (i + 0.5) * length
        r = min(half, length / 2) * rng.uniform(0.7, 1.0)
        cv.ellipse(mx, middle, r, r, "N")
        cv.ellipse(mx, middle, r - 3, r - 3, ".")
    cv.rect(mx - 2, mx + 2, top, bottom, "h")
