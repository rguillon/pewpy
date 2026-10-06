"""How a core's and a part's plans become 3D."""

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.boss_candidates.sculpting import Shaping


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


def part_shaping(cv: Canvas) -> Shaping:
    """Tell how a part's plan becomes 3D.

    Flat underneath (it stands on the core), its dome or glowing core raised, its barrels at half its height.
    """
    top = max(2, min(5, round(min(cv.w, cv.h) * 0.2)))
    return Shaping(
        roles={"S": "raised", "G": "raised", "k": "seam", "r": "gun"},
        tiers={"S": 1, "G": 1},
        top=top,
        bottom=1,
        tier_height=2,
        gun=top // 2,
        fill="t",
        plating="hHNt",
    )
