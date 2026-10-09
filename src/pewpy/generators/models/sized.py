"""One new model of a given size: a ship (an enemy's or the player's), or a whole boss (see pewpy.generators.models).

The size is in world units, across and up the screen (a model's "size", see pewpy.graphics.models.drawing_size). A ship
is made several times from parts picked for that size, a boss scaled towards it, and the one nearest it is kept.
"""

import math

from pewpy import config
from pewpy.generators.models.bosses.selection import boss
from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.ships.selection import build, finish

ATTEMPTS = 12  # bosses made for each one kept
SHIP_ATTEMPTS = 40  # ships made for each one kept: the nearest the size's shape
DECIMALS = 4  # a size's, in world units
AREA_PER_PART = 600  # square cubes of a boss's core for each destroyable part (placeholder)
MIN_PARTS = 2
MAX_PARTS = 12

Size = tuple[float, float]


def cubes(size: Size) -> Size:
    """Return how many cubes (config.MODEL_VOXEL) a size is, across and up."""
    return size[0] / config.MODEL_VOXEL, size[1] / config.MODEL_VOXEL


def rounded(size: Size) -> list[float]:
    """Return a size as a model file writes it."""
    return [round(size[0], DECIMALS), round(size[1], DECIMALS)]


def miss(made: tuple[float, float], wanted: tuple[float, float]) -> float:
    """Tell how far a size is from the one wanted: 0 when it's the same, more the farther (bigger or smaller)."""
    return sum(abs(math.log(have / want)) for have, want in zip(made, wanted, strict=True))


def sized_ship(rng: Rng, size: Size, *, player: bool = False) -> dict:
    """Make a ship's drawing about `size`, of any kind (an enemy's, or the player's), with that "size"."""
    wanted = cubes(size)
    made = min(
        (build(rng, wanted, player=player) for _ in range(SHIP_ATTEMPTS)), key=lambda ship: miss(ship.size(), wanted)
    )
    return {**finish(rng, made, player=player)(), "size": rounded(size)}


def parts_for(size: Size) -> int:
    """Return how many destroyable parts a boss whose core is `size` has: one per AREA_PER_PART, in pairs.

    At least MIN_PARTS, at most MAX_PARTS.
    """
    columns, rows = cubes(size)
    pairs = round(columns * rows / (2 * AREA_PER_PART))
    return max(MIN_PARTS, min(MAX_PARTS, 2 * pairs))


def sized_boss(rng: Rng, size: Size, *, lopsided: bool = False) -> dict:
    """Make a boss whose core is about `size`, with its parts (as many as `parts_for` that size; see
    pewpy.generators.models.bosses.selection.boss for what it is). Its core's drawing has that "size".
    """  # noqa: D205 - the summary needs two lines
    wanted = cubes(size)
    count = parts_for(size)
    asked = wanted  # trimmed, a core comes out smaller than its canvas: ask for more the next time
    best = None
    for _ in range(ATTEMPTS):
        made = boss(rng, lopsided, (max(21, round(asked[0])), max(16, round(asked[1]))), count)
        if made is None:
            continue
        have = made.size
        off = miss(have, wanted)
        if best is None or off < best[0]:
            best = (off, made)
        asked = (asked[0] * wanted[0] / have[0], asked[1] * wanted[1] / have[1])
    if best is None:
        msg = f"no boss could be made {size[0]:.3f} x {size[1]:.3f}"
        raise ValueError(msg)
    drawings = best[1].make()  # only the one kept is built in 3D
    return {**drawings, "core": {**drawings["core"], "size": rounded(size)}}
