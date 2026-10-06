"""Making bosses from the kit, and keeping the most different ones."""

import math
import random
from collections.abc import Callable

from pewpy.tools.boss_candidates.archetypes import BOSS_ARCHETYPES, SIZES, finish
from pewpy.tools.boss_candidates.parts import mount, part, socket, stand
from pewpy.tools.candidates.kit import weapons
from pewpy.tools.candidates.kit.hulls import Hull
from pewpy.tools.candidates.kit.ship import Ship
from pewpy.tools.common.geometry import Rng
from pewpy.tools.common.palette import GREYS, palette, pick_colors
from pewpy.tools.common.variety import features, most_different

LOPSIDED_SHARE = 0.2
MIN_WEAPONS = 5  # on a boss, its parts' and its core's
LARGEST = (115, 95)  # a boss's columns and rows, at most (115: half the screen)
FLAMES = (6, 12)  # its flames' length, in cubes
PART_SCALE = 60  # a part's size grows with its boss's width: this many columns wide, its parts are the kit's size


def boss(rng: Rng, lopsided: bool) -> tuple[list[float], Callable[[], dict]] | None:
    """Make a boss: its features (for telling bosses apart), and what makes its drawings.

    The drawings are {"core": ..., "parts": [(drawing, x, y)]}, (x, y) in cubes from the core's middle (x right, y up
    the screen); only the bosses kept get their parts built.
    """
    size = rng.choices(list(SIZES), [share for share, _, _ in SIZES.values()])[0]
    _, scale, reach = SIZES[size]
    kind = rng.choice(list(BOSS_ARCHETYPES))
    core, body = BOSS_ARCHETYPES[kind](rng, scale, reach)
    finish(rng, core, body, lopsided)
    width, length = core.size()
    if width > LARGEST[0] or length > LARGEST[1]:
        return None
    # Each part's own seed: a part and its mirror image are the same, and built only if the boss is kept.
    spots = [
        (part_kind, px, y, seed)
        for part_kind, x, y, mirrored in mount(rng, core, not lopsided, size)
        for seed in [rng.random()]
        for px in [x] + ([-x] if mirrored else [])
    ]
    colors = palette(GREYS, pick_colors(rng))
    flame = rng.randint(*FLAMES)
    arming = rng.random()
    left, back = min(x for x, _, _ in core.cells), min(y for _, y, _ in core.cells)

    def middle(x: float, y: float) -> tuple[float, float]:
        """From the core's middle, in cubes, y up the screen (its tail is the drawing's first row)."""
        return x - left - (width - 1) / 2, (length - 1) / 2 - (y - back)

    def make() -> dict:
        built = [(part(random.Random(seed), name, width / PART_SCALE), x, y) for name, x, y, seed in spots]
        _arm(random.Random(arming), core, body, sum(len(piece.weapons) for piece, _, _ in built))
        pieces = [stand(core, piece, x, y) for piece, x, y in built]  # on the core once it's armed: over its turrets
        for piece, _, _ in pieces:
            socket(core, piece)
        drawn = [(piece.drawing(colors, flame), *middle(x, y)) for piece, x, y in pieces]
        return {"core": core.drawing(colors, flame), "parts": drawn}

    placed = [middle(x, y) for _, x, y, _ in spots]
    return _features(core, kind, placed, width), make


def _arm(rng: Rng, core: Ship, body: Hull, armed: int) -> None:
    """Put turrets along the core's spine until the boss has MIN_WEAPONS with its parts' `armed`."""
    for share in (0.35, 0.55, 0.75, 0.25, 0.65):
        if len(core.weapons) + armed >= MIN_WEAPONS:
            return
        weapons.turret(rng, core, body, round(body.length * share))


def _features(core: Ship, kind: str, parts: list[tuple[float, float]], width: int) -> list[float]:
    """For telling bosses apart: the outline and size (like the enemies), the kind, the parts and their spread."""
    kinds = [0.8 * (name == kind) for name in BOSS_ARCHETYPES]
    spread = max((math.hypot(x, y) for x, y in parts), default=0.0) / max(width, 1)
    return [*features(core.plan(), core.symmetric), *kinds, len(parts) / 6, 2 * spread, 3 * width / LARGEST[0]]


def generate(count: int, seed: int, pool_factor: int) -> list[dict]:
    """Generate `count` bosses, keeping the most different of `pool_factor` times as many; a share lopsided."""
    rng = random.Random(seed)
    lopsided = round(count * LOPSIDED_SHARE)
    kept = []
    for group, wanted in ((False, count - lopsided), (True, lopsided)):
        pool = [made for _ in range(wanted * pool_factor) if (made := boss(rng, group)) is not None]
        if pool and wanted:
            kept += [make() for make in most_different(pool, wanted)]
    rng.shuffle(kept)
    return kept
