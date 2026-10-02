"""The generator part."""

import math

from pewpewdev.tools.candidates.canvas import Canvas, Rng


def part_generator(rng: Rng, cv: Canvas) -> None:
    mx, my = cv.w // 2, cv.h / 2
    r = min(cv.w, cv.h) / 2 - 1
    for angle in range(0, 360, 90 if rng.random() < 0.5 else 60):  # fins
        a = math.radians(angle)
        cv.line(mx, my, mx + (r + 1) * math.cos(a), my + (r + 1) * math.sin(a), "W")
    cv.ellipse(mx, my, r * 0.7, r * 0.7, "t")
    cv.ellipse(mx, my, r * 0.35, r * 0.35, "G")  # the glowing core
