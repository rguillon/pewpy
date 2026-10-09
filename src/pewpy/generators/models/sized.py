"""One new model of a given size: a ship (the player's, an enemy's or a boss), see pewpy.generators.models.

The size is in world units, across and up the screen (a model's "size", see pewpy.graphics.models.drawing_size). A ship
is framed several times (its hull, wings and engines, made to that size), the frame nearest it finished (its cockpit,
weapons, details...). Enemies and bosses are made the same way: only the size differs, which sets the chance of
destroyable parts.
"""

import random

from pewpy import config
from pewpy.generators.models.common.geometry import Rng, miss
from pewpy.generators.models.ships.placing import Maker, nose_room
from pewpy.generators.models.ships.selection import Asked, finish, maker

ATTEMPTS = 4  # tries (each framed twice, see _aimed) for each ship (or boss) kept: the nearest the size *(placeholder)*
MIN_WEAPONS = 5  # a boss's at least, its parts' and its own
DECIMALS = 4  # a size's, in world units
PARTS_FROM = 300  # square cubes: a model smaller has no destroyable parts... *(placeholder)*
PARTS_ALWAYS = 1350  # ...one this big or bigger always has (every boss), the chance growing between *(placeholder)*
AREA_PER_PART = 600  # square cubes of a model for each destroyable part (placeholder)
MIN_PARTS = 2
MAX_PARTS = 12

Size = tuple[float, float]


def cubes(size: Size) -> Size:
    """Return how many cubes (config.MODEL_VOXEL) a size is, across and up."""
    return size[0] / config.MODEL_VOXEL, size[1] / config.MODEL_VOXEL


def rounded(size: Size) -> list[float]:
    """Return a size as a model file writes it."""
    return [round(size[0], DECIMALS), round(size[1], DECIMALS)]


def parts_chance(size: Size) -> float:
    """Return the chance of a model `size` big having destroyable parts: none under PARTS_FROM square cubes, sure from
    PARTS_ALWAYS, growing with its area between.
    """  # noqa: D205 - the summary needs two lines
    columns, rows = cubes(size)
    return min(1.0, max(0.0, (columns * rows - PARTS_FROM) / (PARTS_ALWAYS - PARTS_FROM)))


def parts_for(size: Size) -> int:
    """Return how many destroyable parts a model `size` big has, if it has some: one per AREA_PER_PART, in pairs.

    At least MIN_PARTS, at most MAX_PARTS.
    """
    columns, rows = cubes(size)
    pairs = round(columns * rows / (2 * AREA_PER_PART))
    return max(MIN_PARTS, min(MAX_PARTS, 2 * pairs))


def sized_model(
    rng: Rng, size: Size, *, player: bool = False, boss: bool = False, lopsided: bool | None = None
) -> dict:
    """Make a model about `size`: the player's ship (`player`), an enemy or a boss (`boss`), all the same way.

    Whether it has destroyable parts depends on its size alone (see parts_chance), but for the game's rules: the
    player's ships never have any, a boss always does; a boss has at least MIN_WEAPONS weapons, anything else one.
    Lopsided or symmetric as asked (`lopsided`), else either. Return its drawings (see
    pewpy.generators.models.ships.ship.Ship.drawing), its own with that "size".
    """
    parts = 0 if player else parts_for(size) if boss or rng.random() < parts_chance(size) else 0
    symmetric = None if lopsided is None else not lopsided
    made = _sized(rng, size, player=player, asked=Asked(parts, symmetric, MIN_WEAPONS if boss else 1))
    return {**made, "core": {**made["core"], "size": rounded(size)}}


def _aimed(seed: int, wanted: Size, framed: Size, player: bool, asked: Asked) -> Maker:
    """Frame a ship from a seed, then again from the same seed aimed to make up for how far off the first one came."""
    first = maker(random.Random(seed), wanted, player=player, asked=asked)
    have = first.frame().size()
    aim = (wanted[0] * framed[0] / have[0], wanted[1] * framed[1] / have[1])
    second = maker(random.Random(seed), aim, player=player, asked=asked)
    second.frame()
    return min((first, second), key=lambda made: miss(made.ship.size(), framed))


def _sized(rng: Rng, size: Size, *, player: bool, asked: Asked) -> dict:
    """Make a ship about `size`: framed a few times, the frame nearest that size finished; return its drawings.

    Each try is framed, then framed again from the same choices, aimed as much off the size as the first frame came
    out off it the other way (see `_aimed`). A frame has no guns on its nose yet: it's compared with the size less the
    room left for them (see placing.nose_room).
    """
    wanted = cubes(size)
    framed = (wanted[0], max(1.0, wanted[1] - nose_room(wanted[1])))
    makers = [_aimed(rng.getrandbits(32), wanted, framed, player, asked) for _ in range(ATTEMPTS)]
    best = min(makers, key=lambda made: miss(made.ship.size(), framed))
    return finish(rng, best.dress(), player=player)()
