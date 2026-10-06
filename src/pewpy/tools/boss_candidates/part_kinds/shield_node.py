"""The shield node part."""

import math

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def part_shield_node(_rng: Rng, cv: Canvas) -> None:
    """Draw a hexagonal shield projector, glowing in the middle."""
    mx, my, r = cv.w / 2 - 0.5, cv.h / 2 - 0.5, min(cv.w, cv.h) / 2 - 0.5
    hexagon = [
        (mx + r * math.cos(math.radians(30 + 60 * i)), my + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)
    ]
    cv.polygon(hexagon, "N")
    cv.polygon([(mx + (x - mx) * 0.7, my + (y - my) * 0.7) for x, y in hexagon], "t")
    cv.ellipse(mx, my, r * 0.3, r * 0.3, "G")
