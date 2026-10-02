"""The drill part."""

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_drill(rng: Rng, cv: Canvas) -> None:
    mx = cv.w // 2
    cv.rect(mx - cv.w // 3, mx + cv.w // 3, 0, cv.h * 0.3, "t")
    cv.polygon([(mx - cv.w / 2.6, cv.h * 0.3), (mx + cv.w / 2.6, cv.h * 0.3), (mx, cv.h - 0.5)], "h")
    rows = set(range(round(cv.h * 0.35), cv.h, 2))  # the thread
    for x, y in cv.cells_of("h"):
        if y in rows:
            cv.set(x, y, "W")
