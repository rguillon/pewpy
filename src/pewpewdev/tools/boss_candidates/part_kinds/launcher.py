"""The launcher part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_launcher(rng: Rng, cv: Canvas) -> None:
    cv.rect(1, cv.w - 2, 1, cv.h - 2, "t")
    for y in range(2, cv.h - 2, 3):
        for x in range(2, cv.w - 2, 3):
            cv.set(x, y, "r")  # a tube
    cv.rect(1, cv.w - 2, cv.h - 2, cv.h - 2, "N")
