"""The radar part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_radar(rng: Rng, cv: Canvas) -> None:
    """A dish on a mast."""
    mx = cv.w / 2 - 0.5
    cv.rect(mx - 1, mx + 1, cv.h * 0.4, cv.h - 1, "t")
    cv.ellipse(mx, cv.h * 0.35, cv.w / 2 - 0.5, cv.h * 0.3, "W")
    cv.ellipse(mx, cv.h * 0.35, 1.2, 1.2, "S")
