"""The flak part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_flak(_rng: Rng, cv: Canvas) -> None:
    """Draw a square mount with four short barrels."""
    cv.rect(1, cv.w - 2, 1, cv.h * 0.6, "t")
    for x in (cv.w * 0.25, cv.w * 0.42, cv.w * 0.58, cv.w * 0.75):
        cv.line(x, cv.h * 0.6, x, cv.h - 1, "r")
