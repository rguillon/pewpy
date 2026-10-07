"""How a core's plan becomes 3D."""

from pewpy.makers.bosses.canvas import Canvas
from pewpy.makers.bosses.sculpting import Shaping


def core_shaping(cv: Canvas) -> Shaping:
    """Tell how a core's plan becomes 3D.

    Lower decks (T), the superstructure on them (S) with the bridge (c), its sensor (R) on top; thicker on bigger
    bosses.
    """
    top = max(3, min(7, round(cv.w * 0.06)))
    return Shaping(
        roles={
            "T": "raised",
            "S": "raised",
            "c": "raised",
            "R": "raised",
            "k": "seam",
            "g": "seam",
            "w": "wing",
            "W": "wing",
            "q": "wing",
            "r": "gun",
        },
        tiers={"T": 1, "S": 2, "c": 2, "R": 3},
        top=top,
        bottom=top - 1,
        edge=1,
        tier_height=2,
        wing=2,
        lift=0.04,
        fill="T",
    )
