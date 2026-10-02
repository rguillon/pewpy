"""The claw part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_claw(rng: Rng, cv: Canvas) -> None:
    """A heavy claw: a base and two curved pincers."""
    mx = cv.w // 2
    cv.rect(mx - cv.w * 0.3, mx + cv.w * 0.3, 0, cv.h * 0.35, "t")
    for side in (-1, 1):
        cv.polygon([(mx + side * 1, cv.h * 0.35), (mx + side * cv.w * 0.45, cv.h * 0.35), (mx + side * cv.w * 0.25, cv.h - 0.5),
                    (mx + side * 0.5, cv.h * 0.6)], "N")  # fmt: skip
