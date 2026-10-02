"""The emitter part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_emitter(_rng: Rng, cv: Canvas) -> None:
    """Draw a beam emitter: a long prism with a glowing tip."""
    mx = cv.w // 2
    cv.polygon([(mx - cv.w * 0.4, 0), (mx + cv.w * 0.4, 0), (mx + 1.5, cv.h - 3), (mx - 1.5, cv.h - 3)], "t")
    cv.rect(mx - 1, mx + 1, cv.h - 3, cv.h - 1, "G")
    cv.rect(mx, mx, 1, cv.h - 4, "S")
