"""The segmented core."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def core_segmented(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    """Draw blocks of different widths, joined by a neck."""
    count = rng.randint(2, 4)
    length = cv.h / count
    for i in range(count):
        width = rng.uniform(max(1.0, half * 0.5), half)
        cv.rect(mx - width, mx + width, i * length + (0.8 if i else 0), (i + 1) * length - 1, "h")
    cv.rect(mx - 1, mx + 1, 0, cv.h - 1, "h")
