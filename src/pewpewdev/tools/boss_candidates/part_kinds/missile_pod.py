"""The missile pod part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_missile_pod(rng: Rng, cv: Canvas) -> None:
    """A cluster of missile tubes, their warheads showing."""
    mx, my = cv.w / 2 - 0.5, cv.h / 2 - 0.5
    cv.ellipse(mx, my, cv.w / 2 - 0.5, cv.h / 2 - 0.5, "N")
    for y in range(2, cv.h - 1, 3):
        for x in range(2, cv.w - 1, 3):
            if cv.get(x, y) == "N":
                cv.set(x, y, "G")
