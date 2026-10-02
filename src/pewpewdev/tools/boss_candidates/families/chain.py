"""The chain family."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def chain(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Segments linked in a column, like a train of hulls."""
    count = rng.randint(3, 5)
    length = (bottom - top) / count
    for i in range(count):
        middle = top + (i + 0.5) * length
        width = half * rng.uniform(0.5, 1.0)
        cv.ellipse(mx, middle, width, length * 0.42, "h" if i % 2 else "T")
    cv.rect(mx - 1, mx + 1, top, bottom, "N")
