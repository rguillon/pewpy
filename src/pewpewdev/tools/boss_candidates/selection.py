"""Making bosses, and keeping the most different ones."""

import math
import random
from collections.abc import Callable

from pewpewdev.tools.boss_candidates.core import LOPSIDED_SHARE, armor, core, engine_bank, paint, superstructure
from pewpewdev.tools.boss_candidates.families import FAMILIES
from pewpewdev.tools.boss_candidates.mounting import mount, part, socket
from pewpewdev.tools.boss_candidates.palette import CORE_GREYS, PART_GREYS, palette
from pewpewdev.tools.boss_candidates.shaping import core_shaping, part_shaping
from pewpewdev.tools.candidates.canvas import Canvas, Rng
from pewpewdev.tools.candidates.details import bands, markings, panel_lines, trim, wing_edges
from pewpewdev.tools.candidates.layers import layered_drawing
from pewpewdev.tools.candidates.palette import ACCENTS, HULL_TINTS, LIVERIES
from pewpewdev.tools.candidates.selection import features, most_different
from pewpewdev.tools.candidates.shaping import engines_at_height, lifted, sculpt


def boss(rng: Rng, lopsided: bool) -> tuple[list[float], Callable[[], dict]] | None:
    """Make a boss: its features (for telling bosses apart), and what makes its drawings.

    The drawings are {"core": ..., "parts": [(drawing, x, y)]} (only the bosses kept are built in 3D).
    """
    cv, family, size = core(rng, lopsided)
    trim(cv, not lopsided)
    if cv.w < 20 or cv.h < 15:
        return None
    bands(rng, cv)
    wing_edges(cv)
    panel_lines(rng, cv)
    armor(rng, cv)
    superstructure(rng, cv)
    scheme = paint(rng, cv)
    markings(rng, cv)
    parts = []
    for part_kind, x, y, mirrored in mount(rng, cv, not lopsided, size):
        part_cv = part(rng, part_kind, cv.w)
        socket(cv, x, y, part_cv, mirrored)
        parts.append((part_cv, x, y, mirrored))
    engines = engine_bank(rng, cv)
    if not lopsided:
        for row in cv.cells:
            for x in range(cv.w // 2):
                row[cv.w - 1 - x] = row[x]
        engines = [{**engine, "x": x} for engine in engines for x in {engine["x"], cv.w - 1 - engine["x"]}]
    tint = HULL_TINTS[rng.choice(list(HULL_TINTS))]
    accent, livery = rng.choice(list(ACCENTS)), rng.choice(LIVERIES)
    # From the core's middle, in cubes, y up the screen.
    spots = [(part_cv, px, y) for part_cv, x, y, mirrored in parts for px in [x] + ([cv.w - 1 - x] if mirrored else [])]
    placed = [(part_cv, px - (cv.w - 1) / 2, (cv.h - 1) / 2 - y) for part_cv, px, y in spots]

    def make() -> dict:
        cells, heights = sculpt(cv, core_shaping(cv))
        core_drawing = {
            **layered_drawing(cells, cv, palette(CORE_GREYS, tint, accent, livery)),
            "engines": engines_at_height(engines, heights),
        }
        colors = palette(PART_GREYS, tint, accent, livery)
        shaped = {id(part_cv): sculpt(part_cv, part_shaping(part_cv))[0] for part_cv, _, _ in spots}
        drawings = []
        for (part_cv, px, y), (_, x, up) in zip(spots, placed, strict=True):
            # Standing on the core's top there: its lowest cubes just above the core's highest (no overlap).
            lift = heights.get((px, y), (0, 0))[1] + 1 + part_shaping(part_cv).bottom
            drawings.append((layered_drawing(lifted(shaped[id(part_cv)], lift), part_cv, colors), x, up))
        return {"core": core_drawing, "parts": drawings}

    return _features(cv, family, scheme, placed, not lopsided), make


def _features(cv: Canvas, family: str, scheme: str, parts: list, symmetric: bool) -> list[float]:
    """For telling bosses apart: the outline and size (like the enemies), the family, the paint, the parts."""
    families = [0.8 * (name in family.split("+")) for name in FAMILIES]
    spread = max((math.hypot(x, y) for _, x, y in parts), default=0.0) / max(cv.w, 1)
    return [
        *features(cv.rows(), symmetric),
        *families,
        0.5 * (scheme != "plain"),
        len(parts) / 6,
        2 * spread,
        3 * cv.w / 115,  # bigger ones stand apart more than the enemies' feature does at this size
    ]


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
