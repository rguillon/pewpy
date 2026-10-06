"""The station family."""

import math

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.common.geometry import Rng


def station(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Draw an octagonal ring around a hub, joined by spokes."""
    my, r = (top + bottom) / 2, min(half, (bottom - top) / 2)
    angles = [math.pi / 8 + i * math.pi / 4 for i in range(8)]
    cv.polygon([(mx + r * math.cos(a), my + r * math.sin(a)) for a in angles], "N")
    cv.polygon([(mx + (r - 4) * math.cos(a), my + (r - 4) * math.sin(a)) for a in angles], ".")
    cv.ellipse(mx, my, r * 0.35, r * 0.35, "h")
    spokes = rng.choice((2, 3, 4, 6))
    for i in range(spokes):
        a = math.pi / 2 + i * 2 * math.pi / spokes
        for dx in (0, 1):
            cv.line(mx + dx, my, mx + dx + r * math.cos(a), my + r * math.sin(a), "h")
