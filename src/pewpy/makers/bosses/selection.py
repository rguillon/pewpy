"""Making bosses."""

from collections.abc import Callable
from typing import NamedTuple

from pewpy.makers.bosses.core import armor, core, engine_bank, paint, superstructure
from pewpy.makers.bosses.details import bands, join, markings, panel_lines, trim, wing_edges
from pewpy.makers.bosses.greebles import greeble
from pewpy.makers.bosses.mounting import middle_row, mount, part, socket
from pewpy.makers.bosses.sculpting import Cells, engines_at_height, lifted, sculpt
from pewpy.makers.bosses.shaping import core_shaping
from pewpy.makers.bosses.weapons import CORE_GUNS, MIN_WEAPONS, core_guns
from pewpy.makers.common.drawing import layered_drawing, numbered_weapons
from pewpy.makers.common.geometry import Rng
from pewpy.makers.common.palette import CORE_GREYS, PART_GREYS, palette, pick_colors
from pewpy.makers.components import Piece


def boss(
    rng: Rng, lopsided: bool, cubes: tuple[int, int] | None = None, parts_wanted: int | None = None
) -> "Made | None":
    """Make a boss: what makes its drawings, its core's size; None if it came out too small.

    Its core `cubes` (columns, rows) or any size, `parts_wanted` parts or as many as its size has room for. The drawings
    are {"core": ..., "parts": [(drawing, x, y)], "groups": [each part's group], "kinds": [each part's kind]} (only
    the bosses kept are built in 3D): the parts of a group (a pair mirroring each other) share one drawing.
    """
    cv, _family, size = core(rng, lopsided, cubes)
    trim(cv, not lopsided)
    if cv.w < 20 or cv.h < 15:
        return None
    bands(rng, cv)
    wing_edges(cv)
    panel_lines(rng, cv)
    armor(rng, cv)
    superstructure(rng, cv)
    paint(rng, cv)
    markings(rng, cv)
    parts = []  # (piece, x, y, mirrored, group)
    kinds: dict[int, str] = {}  # each group's kind
    pieces: dict[int, Piece] = {}  # each group's part
    for group, (part_kind, x, y, mirrored) in enumerate(mount(rng, cv, not lopsided, size, parts_wanted)):
        piece = pieces[group] = part(rng, part_kind, cv.w)
        socket(cv, x, y, piece, mirrored)
        parts.append((piece, x, y, mirrored, group))
        kinds[group] = part_kind
    engines = engine_bank(rng, cv)
    if not lopsided:
        for row in cv.cells:
            for x in range(cv.w // 2):
                row[cv.w - 1 - x] = row[x]
        engines = [{**engine, "x": x} for engine in engines for x in {engine["x"], cv.w - 1 - engine["x"]}]
    join(cv, not lopsided)  # no piece of the hull left floating
    armed = sum(len(piece.weapons) * (2 if mirrored else 1) for piece, _, _, mirrored, _ in parts)
    guns = core_guns(cv, max(CORE_GUNS, MIN_WEAPONS - armed), not lopsided)
    colors = pick_colors(rng)
    # Each part's middle on the core, from its top-left; then from its middle, in cubes, y up the screen.
    spots = [(px, y, group) for _, x, y, mirrored, group in parts for px in [x] + ([cv.w - 1 - x] if mirrored else [])]
    placed = [(px - (cv.w - 1) / 2, (cv.h - 1) / 2 - y) for px, y, _ in spots]

    def make() -> dict:
        shaping = core_shaping(cv)
        cells, heights = sculpt(cv, shaping)
        surface = greeble(cv, cells, heights, symmetric=not lopsided, level=shaping.top)
        core_drawing = {
            **layered_drawing(cells, cv.w, cv.h, palette(CORE_GREYS, colors)),
            "engines": engines_at_height(engines, heights) + surface.engines,
            "weapons": numbered_weapons(guns + surface.weapons),
        }
        part_colors = palette(PART_GREYS, colors)
        drawings: dict[int, dict] = {}
        for group in dict.fromkeys(group for _, _, group in spots):
            piece = pieces[group]
            middle = middle_row(piece)
            # Standing on the core: its lowest cubes just above the core's highest under any of its group's parts.
            lift = 1 + max(
                heights.get((px + dx, y + dy - middle), (0, 0))[1]
                for px, y, spot_group in spots
                if spot_group == group
                for dx, dy in piece.footprint()
            )
            drawings[group] = _part_drawing(piece, lift, part_colors)
        return {
            "core": core_drawing,
            "parts": [(drawings[group], x, up) for (_, _, group), (x, up) in zip(spots, placed, strict=True)],
            "groups": [group for _, _, group in spots],
            "kinds": [kinds[group] for _, _, group in spots],
        }

    return Made(make, (cv.w, cv.h))


class Made(NamedTuple):
    """A boss made: what builds its drawings in 3D, its core's columns and rows (its drawing's, without building it)."""

    make: Callable[[], dict]
    size: tuple[int, int]


def _part_drawing(piece: Piece, lift: int, colors: dict) -> dict:
    """Return a destroyable part's 3D drawing: its built-in part `lift` cubes above the middle plane, its weapons."""
    half = max(abs(x) for x, _ in piece.footprint())
    length = max(y for _, y in piece.footprint()) + 1
    cells: Cells = {(x + half, y, -z): char for (x, y, z), char in piece.cells.items()}
    drawing = layered_drawing(lifted(cells, lift), 2 * half + 1, length, colors)
    weapons = numbered_weapons([(kind, x + half, y) for kind, x, y, _ in piece.weapons])
    return {**drawing, "weapons": weapons} if weapons else drawing
