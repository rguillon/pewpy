"""Industrial ships: a core hull (cores/) with attachments (attachments/), symmetric or lopsided.

They are sculpted from their plan.
"""

from pewpewdev.tools.candidates.canvas import Canvas, Rng
from pewpewdev.tools.candidates.industrial.attachments import ATTACHMENTS
from pewpewdev.tools.candidates.industrial.cores import CORES
from pewpewdev.tools.candidates.shaping import Shaping


def industrial(rng: Rng, lopsided: bool) -> tuple[Canvas, bool]:
    """Draw an industrial ship's plan; return it and whether it's symmetric."""
    kind = rng.random()
    if kind < 0.2:  # small drones and fighters
        width, height = rng.randrange(7, 14, 2), rng.randint(7, 13)
    elif kind < 0.8:
        width, height = rng.randrange(13, 24, 2), rng.randint(11, 22)
    else:  # heavies
        width, height = rng.randrange(23, 36, 2), rng.randint(19, 34)
    cv = Canvas(width, height)
    mx = width // 2 + (rng.choice((-1, 1)) * rng.randint(0, max(1, width // 6)) if lopsided else 0)
    half = max(1, round(width * rng.uniform(0.12, 0.3)))
    rng.choice(CORES)(rng, cv, mx, half)
    edge = max(1, mx - half - 1)
    for _ in range(rng.randint(1, 3 if width > 12 else 2)):
        side = "one" if lopsided and rng.random() < 0.6 else "both"
        rng.choice(ATTACHMENTS)(rng, cv, edge, side)
    if lopsided and rng.random() < 0.5:  # so lopsided ships lean either way
        cv.cells = [row[::-1] for row in cv.cells]
    return cv, not lopsided


def industrial_shaping(cv: Canvas) -> Shaping:
    """How an industrial ship's plan becomes 3D: its hull thicker on bigger ships."""
    top = max(1, min(4, round(min(cv.w, cv.h) * 0.16)))
    return Shaping(
        roles={
            "S": "raised",
            "c": "raised",
            "R": "raised",
            "k": "seam",
            "w": "wing",
            "W": "wing",
            "q": "wing",
            "t": "pod",
            "r": "gun",
        },
        tiers={"S": 1, "c": 1, "R": 2},
        top=top,
        bottom=max(1, top - 1),
        pod=max(1, top - 1),
    )
