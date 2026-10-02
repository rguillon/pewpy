"""The cannon part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_cannon(_rng: Rng, cv: Canvas) -> None:
    """Draw a cannon: a wide breech and a long barrel with a muzzle."""
    mx = cv.w // 2
    cv.rect(mx - cv.w // 3, mx + cv.w // 3, 0, cv.h * 0.55, "t")
    cv.rect(mx - 1, mx + 1, cv.h * 0.55, cv.h - 1, "r")
    cv.rect(mx - 2, mx + 2, cv.h - 3, cv.h - 1, "N")  # the muzzle
    cv.rect(mx - cv.w // 3, mx + cv.w // 3, 1, 2, "k")
