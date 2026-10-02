"""The turret part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_turret(rng: Rng, cv: Canvas) -> None:
    mx, my = cv.w // 2, cv.h * 0.45
    r = min(cv.w, cv.h) * 0.35
    cv.ellipse(mx, my, r + 1, r + 1, "N")
    cv.ellipse(mx, my, r, r, "t")
    cv.ellipse(mx, my, r * 0.5, r * 0.5, "S")
    barrels = rng.choice((1, 2, 3))
    for i in range(barrels):
        x = mx + (i - (barrels - 1) / 2) * 2
        cv.line(x, my, x, cv.h - 1, "r")
