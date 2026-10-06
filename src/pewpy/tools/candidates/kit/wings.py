"""The wings: hardcoded outlines of a left wing, stretched to its span and chord.

An outline is a polygon of (share of the span from the root to the tip, share of the root's chord from its trailing
edge towards the nose). A wing is one cube thick (two at the root), rises or droops towards its tip, and is painted: a
light leading edge, dark flaps along the trailing edge, a marking on its tip. Canards and tailplanes are small wings.
"""

from dataclasses import dataclass

from pewpy.tools.candidates.kit.ship import Ship
from pewpy.tools.common.geometry import Point, inside

WINGS: dict[str, list[Point]] = {
    "swept": [(0, 0), (0, 1), (1, 0.2), (1, -0.15)],
    "delta": [(0, -0.05), (0, 1.15), (1, 0.05), (1, -0.05)],
    "forward": [(0, 0.05), (0, 0.85), (1, 1.2), (1, 0.85)],
    "straight": [(0, 0), (0, 1), (1, 0.9), (1, 0.3)],
    "cranked": [(0, -0.05), (0, 1.15), (0.35, 0.85), (1, 0.15), (1, -0.05)],
    "ogival": [(0, -0.1), (0, 1.2), (0.3, 0.95), (0.65, 0.55), (1, 0.12), (1, -0.05)],
    "bat": [(0, 0), (0, 1), (1, 0.55), (1, 0.1), (0.7, 0.3), (0.4, 0.05)],
    "trapezoid": [(0, 0), (0, 1), (1, 0.75), (1, 0.35)],
    "scythe": [(0, 0.1), (0, 1), (0.6, 0.75), (1, 0.15), (1, -0.25), (0.55, 0.2)],
    "box": [(0, 0), (0, 1), (1, 1), (1, 0)],
}


@dataclass
class Wing:
    """A wing placed on a ship: its tip's cells, from the trailing edge forward, and where its leading edge is."""

    tip: list[tuple[int, int, int]]
    root_x: int
    leading: dict[int, tuple[int, int]]  # x -> (y of the leading edge, z)


def wing(
    ship: Ship,
    outline: str,
    root_x: int,
    trailing_y: int,
    span: int,
    chord: int,
    z: int,
    rise: float = 0.0,
    *,
    tip_marking: bool = False,
    char: str = "w",
) -> Wing:
    """Build a left wing (and its mirror image) from `root_x` outwards (x more negative), `span` cubes long.

    Its root runs `chord` cubes from `trailing_y` towards the nose, at height `z`; `rise` cubes up per cube out.
    """
    points = WINGS[outline]
    cells: dict[tuple[int, int], int] = {}
    for i in range(span + 1):
        for y in range(trailing_y - chord, trailing_y + 2 * chord + 1):
            u, v = (i + 0.5) / (span + 1), (y - trailing_y + 0.5) / chord
            if inside(u, v, points):
                cells[i, y] = z + round(i * rise)
    tip_i = max((i for i, _ in cells), default=0)
    leading: dict[int, tuple[int, int]] = {}
    for (i, y), height in cells.items():
        x = root_x - i
        thick = range(height - 1, height + 1) if i < 2 else range(height, height + 1)
        if (i, y + 1) not in cells:
            paint = "W"  # the leading edge
            if x not in leading or y > leading[x][0]:
                leading[x] = (y, height)
        elif (i, y - 1) not in cells:
            paint = "k"  # the flaps
        elif tip_marking and i >= tip_i - 1:
            paint = "q"
        else:
            paint = char if (i + y) % 4 else "W"
        for level in thick:
            ship.put(x, y, level, paint, over=False)
    tip = sorted((root_x - i, y, height) for (i, y), height in cells.items() if i == tip_i)
    return Wing(tip, root_x, leading)
