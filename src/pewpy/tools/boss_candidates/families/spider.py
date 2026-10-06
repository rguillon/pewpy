"""The spider family."""

import math

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def spider(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw a round body with legs reaching out, each ending in a claw."""
    my = (top + bottom) / 2
    body = min(half, (bottom - top) / 2) * rng.uniform(0.3, 0.45)
    legs = rng.randint(2, 4)
    for i in range(legs):
        a = math.radians(-60 + 120 * i / max(1, legs - 1))  # from forward-left to back-left
        end_x, end_y = mx - half * math.cos(a) * 0.95, my - (bottom - top) * 0.45 * math.sin(a)
        knee_x, knee_y = (mx + end_x) / 2, (my + end_y) / 2 - 3
        for a0, a1 in (((mx, my), (knee_x, knee_y)), ((knee_x, knee_y), (end_x, end_y))):
            for dx in (0, 1):
                cv.line(a0[0] + dx, a0[1], a1[0] + dx, a1[1], "N", "both")
        cv.ellipse(end_x, end_y, 2, 2, "h")
        cv.set(round(end_x), round(end_y) + 3, "r")
    cv.ellipse(mx, my, body, body * 1.2, "h")
