"""Making bosses, and keeping the most different ones."""

import math
import random
from collections.abc import Callable

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.boss_candidates.core import LOPSIDED_SHARE, armor, core, engine_bank, paint, superstructure
from pewpy.tools.boss_candidates.details import bands, markings, panel_lines, trim, wing_edges
from pewpy.tools.boss_candidates.families import FAMILIES
from pewpy.tools.boss_candidates.greebles import greeble
from pewpy.tools.boss_candidates.mounting import mount, part, socket
from pewpy.tools.boss_candidates.sculpting import Cells, engines_at_height, lifted, sculpt
from pewpy.tools.boss_candidates.shaping import core_shaping, part_shaping
from pewpy.tools.boss_candidates.weapons import CORE_GUNS, MIN_WEAPONS, core_guns, part_weapons
from pewpy.tools.common.drawing import layered_drawing, numbered_weapons
from pewpy.tools.common.geometry import Rng
from pewpy.tools.common.palette import CORE_GREYS, PART_GREYS, palette, pick_colors
from pewpy.tools.common.variety import features, most_different


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
    kinds: dict[int, str] = {}  # a part's kind, by its plan's id
    for part_kind, x, y, mirrored in mount(rng, cv, not lopsided, size):
        part_cv = part(rng, part_kind, cv.w)
        socket(cv, x, y, part_cv, mirrored)
        parts.append((part_cv, x, y, mirrored))
        kinds[id(part_cv)] = part_kind
    engines = engine_bank(rng, cv)
    if not lopsided:
        for row in cv.cells:
            for x in range(cv.w // 2):
                row[cv.w - 1 - x] = row[x]
        engines = [{**engine, "x": x} for engine in engines for x in {engine["x"], cv.w - 1 - engine["x"]}]
    armed = sum(
        len(part_weapons(part_cv, kinds[id(part_cv)])) * (2 if mirrored else 1) for part_cv, _, _, mirrored in parts
    )
    guns = core_guns(cv, max(CORE_GUNS, MIN_WEAPONS - armed), not lopsided)
    colors = pick_colors(rng)
    # From the core's middle, in cubes, y up the screen.
    spots = [(part_cv, px, y) for part_cv, x, y, mirrored in parts for px in [x] + ([cv.w - 1 - x] if mirrored else [])]
    placed = [(part_cv, px - (cv.w - 1) / 2, (cv.h - 1) / 2 - y) for part_cv, px, y in spots]

    def make() -> dict:
        shaping = core_shaping(cv)
        cells, heights = sculpt(cv, shaping)
        greeble(cv, cells, heights, symmetric=not lopsided, level=shaping.top)
        core_drawing = {
            **layered_drawing(cells, cv.w, cv.h, palette(CORE_GREYS, colors)),
            "engines": engines_at_height(engines, heights),
            "weapons": numbered_weapons(guns),
        }
        part_colors = palette(PART_GREYS, colors)
        shaped = {id(part_cv): _part_cells(part_cv) for part_cv, _, _ in spots}
        drawings = []
        for (part_cv, px, y), (_, x, up) in zip(spots, placed, strict=True):
            # Standing on the core's top there: its lowest cubes just above the core's highest (no overlap).
            lift = heights.get((px, y), (0, 0))[1] + 1 + part_shaping(part_cv).bottom
            drawing = layered_drawing(lifted(shaped[id(part_cv)], lift), part_cv.w, part_cv.h, part_colors)
            weapons = numbered_weapons(part_weapons(part_cv, kinds[id(part_cv)]))
            drawings.append(({**drawing, "weapons": weapons} if weapons else drawing, x, up))
        return {"core": core_drawing, "parts": drawings}

    return _features(cv, family, scheme, placed, not lopsided), make


def _part_cells(part_cv: Canvas) -> Cells:
    """Return a part's cubes: sculpted from its plan, then detailed."""
    shaping = part_shaping(part_cv)
    cells, heights = sculpt(part_cv, shaping)
    greeble(part_cv, cells, heights, symmetric=True, level=shaping.top, part=True)
    return cells


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
