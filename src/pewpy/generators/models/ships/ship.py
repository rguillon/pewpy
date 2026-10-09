"""A ship being assembled from the catalog's parts: its cubes, its engines' nozzles, its weapons, as a 3D drawing.

A boss is a ship with destroyable parts: modules standing on it (see modules.py), drawn apart from it. Their places
are reserved: nothing else goes there, nor in front of their barrels.

Parts are placed as they are, or mirrored (the right side's copy of a left wing...). A part only goes where it fits: it
doesn't sink into the ship (but for the overlap its mount allows), it doesn't stand in front of a weapon's barrel nor
behind an engine's nozzle, and its own barrels and nozzles are clear. Nothing else is checked: pieces left apart are
joined by struts as the drawing is written (see models.common.connect).
"""

from dataclasses import dataclass, field

from pewpy.generators.models.common.connect import bridges
from pewpy.generators.models.common.drawing import layered_drawing, numbered_weapons
from pewpy.generators.models.parts import Part

Cell = tuple[int, int, int]  # x across (0 on the ship's axis), y along it (0 at the hull's tail), z up (to the camera)
STRUT = "N"  # the cubes joining pieces left apart


@dataclass(frozen=True)
class Spot:
    """Where a part goes: its origin's place, mirrored across its own middle (`flip`, the right side's copy) or not."""

    x: int
    y: int
    z: int
    flip: bool = False

    def cell(self, cell: Cell) -> Cell:
        """Return where one of the part's cubes goes."""
        x, y, z = cell
        return self.x + (-x if self.flip else x), self.y + y, self.z + z

    def column(self, x: float) -> float:
        """Return where one of the part's x goes (a weapon's or a nozzle's)."""
        return self.x + (-x if self.flip else x)


@dataclass(frozen=True)
class Placed:
    """A part placed on the ship."""

    part: Part
    spot: Spot

    def cells(self) -> dict[Cell, str]:
        """Return its cubes, where they are on the ship."""
        sx, sy, sz = self.spot.x, self.spot.y, self.spot.z
        if self.spot.flip:
            return {(sx - x, sy + y, sz + z): char for (x, y, z), char in self.part.cells.items()}
        return {(sx + x, sy + y, sz + z): char for (x, y, z), char in self.part.cells.items()}


@dataclass
class Ship:
    """The parts placed so far: their cubes (palette characters, see models.common.palette), nozzles and weapons."""

    cells: dict[Cell, str] = field(default_factory=dict)
    nozzles: list[tuple[float, int, float, float]] = field(default_factory=list)  # (x, y, z, width)
    weapons: list[tuple[str, int, int, int]] = field(default_factory=list)  # (kind, x, y, z) of a barrel's tip
    placed: list[Placed] = field(default_factory=list)
    tops: dict[tuple[int, int], int] = field(default_factory=dict)  # the highest cube's z at each (x, y)
    bottoms: dict[tuple[int, int], int] = field(default_factory=dict)  # the lowest's
    destroyable: list[tuple[Part, Spot, int, str]] = field(default_factory=list)  # (module, spot, group, kind)
    _lines: dict[tuple[int, int], tuple[int, int]] = field(default_factory=dict)  # (x, z): the lowest and highest y
    _reserved: set[Cell] = field(default_factory=set)  # the destroyable parts' cubes
    _reserved_weapons: list[tuple[str, int, int, int]] = field(default_factory=list)

    def fits(self, part: Part, spots: list[Spot], overlap: float = 0.0) -> bool:
        """Tell whether a part fits at each of the spots: see the module's description.

        `overlap`: the share of its cubes that may sink into the ship's.
        """
        new: dict[Cell, str] = {}
        for spot in spots:
            new |= Placed(part, spot).cells()
        sunk = sum(cell in self.cells for cell in new)
        if sunk > overlap * len(new) or any(cell in self._reserved for cell in new):
            return False
        lines = dict(self._lines)
        for x, y, z in new:
            low, high = lines.get((x, z), (y, y))
            lines[x, z] = min(low, y), max(high, y)
        weapons = [*self.weapons, *self._reserved_weapons]
        weapons += [_weapon(spot, weapon) for spot in spots for weapon in part.weapons]
        if any(lines.get((x, z), (y, y))[1] > y for _, x, y, z in weapons):  # something in front of a barrel
            return False
        nozzles = [(round(x), y, round(z)) for x, y, z, _ in self.nozzles] + [
            (round(spot.column(x)), spot.y + y, round(spot.z + z)) for spot in spots for x, y, z, _ in part.nozzles
        ]
        return all(lines.get((x, z), (y, y))[0] >= y for x, y, z in nozzles)  # nothing behind a nozzle

    def place(self, part: Part, spots: list[Spot]) -> None:
        """Place a part at each of the spots, the cubes there staying, with its weapons and nozzles."""
        for spot in spots:
            placed = Placed(part, spot)
            self.placed.append(placed)
            self._add(placed.cells())
            self.weapons += [_weapon(spot, weapon) for weapon in part.weapons]
            self.nozzles += [(spot.column(x), spot.y + y, spot.z + z, width) for x, y, z, width in part.nozzles]

    def reserve(self, part: Part, spots: list[Spot], group: int, kind: str) -> None:
        """Stand a destroyable part (a module, see modules.py) at each of the spots: its place kept for it."""
        for spot in spots:
            self.destroyable.append((part, spot, group, kind))
            for x, y, z in Placed(part, spot).cells():
                self._reserved.add((x, y, z))
                low, high = self._lines.get((x, z), (y, y))
                self._lines[x, z] = min(low, y), max(high, y)  # nothing in front of its barrels, nor in its way
            self._reserved_weapons += [_weapon(spot, weapon) for weapon in part.weapons]

    def armed(self) -> int:
        """Return how many weapons it has, its destroyable parts' too."""
        return len(self.weapons) + len(self._reserved_weapons)

    def _add(self, new: dict[Cell, str]) -> None:
        """Add cubes where there are none (the cubes there stay): `put` for many at once, as fast as it goes."""
        cells, tops, bottoms, lines = self.cells, self.tops, self.bottoms, self._lines
        for cell, char in new.items():
            if cell in cells:
                continue
            cells[cell] = char
            x, y, z = cell
            column = (x, y)
            top = tops.get(column)
            if top is None or z > top:
                tops[column] = z
            bottom = bottoms.get(column)
            if bottom is None or z < bottom:
                bottoms[column] = z
            line = lines.get((x, z))
            if line is None:
                lines[x, z] = (y, y)
            elif y < line[0] or y > line[1]:
                lines[x, z] = (min(line[0], y), max(line[1], y))

    def put(self, x: int, y: int, z: int, char: str, *, over: bool = True) -> None:
        """Set a cube; `over=False` keeps what's there."""
        if not over and (x, y, z) in self.cells:
            return
        self.cells[x, y, z] = char
        self.tops[x, y] = max(z, self.tops.get((x, y), z))
        self.bottoms[x, y] = min(z, self.bottoms.get((x, y), z))
        low, high = self._lines.get((x, z), (y, y))
        self._lines[x, z] = min(low, y), max(high, y)

    def size(self) -> tuple[int, int]:
        """Return how many columns and rows the ship covers."""
        xs = [x for x, _, _ in self.cells]
        ys = [y for _, y, _ in self.cells]
        return max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

    def symmetric(self) -> bool:
        """Tell whether its cubes are their own mirror image across its axis."""
        return all((-x, y, z) in self.cells for x, y, z in self.cells)

    def drawing(self, colors: dict, flame_length: int, *, player: bool = False) -> dict:
        """Return the ship as 3D drawings: {"core": its own, "parts": [(each destroyable part's, x, y)], "groups": [each
        part's group: a pair's parts share their drawing], "kinds": [each part's kind]} (no parts: empty lists).

        Its own: its layers, palette, engines (flames out of its tail), weapons (numbered). A part's x and y are where
        its middle is from the ship's, in cubes, y up the screen; it stands at its height on the ship. An enemy points
        down the screen: its tail on the drawing's first row, its flames "towards" the top. A player's
        ship (`player`) points up: its tail on the last row, its flames towards the bottom; it lists no weapons (the
        player's guns don't use them). Pieces left apart are joined by struts, mirrored on a symmetric ship.
        """  # noqa: D205 - the summary needs two lines
        symmetric = self.symmetric()
        xs = [x for x, _, _ in self.cells]
        left = -max(map(abs, xs)) if symmetric else min(xs)  # a symmetric ship's axis in its middle column
        back = min(y for _, y, _ in self.cells)
        width = (max(xs) - left + 1) if not symmetric else 2 * max(map(abs, xs)) + 1
        length = self.size()[1]

        def row(y: float) -> float:  # the drawing's row of a y from the tail
            return length - 1 - (y - back) if player else y - back

        cells = {(x - left, round(row(y)), -z): char for (x, y, z), char in self.cells.items()}  # layers: up is < 0
        mirror = (lambda cell: (width - 1 - cell[0], *cell[1:])) if symmetric else None
        for x, y, z in bridges(cells, mirror):  # every cube touching the others
            cells[x, y, z] = STRUT
        engines = []
        for x, y, z, flame in self.nozzles:
            engine = {
                "x": x - left,
                "y": row(y),
                "width": flame,
                "length": flame_length,
                "towards": "bottom" if player else "top",
            }
            if z:
                engine["z"] = z
            engines.append(engine)
        drawing = {**layered_drawing(cells, width, length, colors), "engines": engines}
        if not player:
            weapons = numbered_weapons([(kind, x - left, y - back) for kind, x, y, _ in self.weapons])
            drawing = {**drawing, "weapons": weapons}
        middle = ((width - 1) / 2, (length - 1) / 2)
        shared: dict[int, dict] = {}  # each group's drawing: a pair's parts share it
        for module, spot, group, _ in self.destroyable:
            shared.setdefault(group, _part_drawing(module, spot.z, colors))
        parts = [
            (
                shared[group],
                spot.x - left - middle[0],
                middle[1] - (spot.y + module.high[1] / 2 - back),  # up the screen
            )
            for module, spot, group, _ in self.destroyable
        ]
        return {
            "core": drawing,
            "parts": parts,
            "groups": [group for _, _, group, _ in self.destroyable],
            "kinds": [kind for _, _, _, kind in self.destroyable],
        }


def _weapon(spot: Spot, weapon: tuple[str, int, int, int]) -> tuple[str, int, int, int]:
    """Return where a part's weapon goes."""
    kind, x, y, z = weapon
    return (kind, *spot.cell((x, y, z)))


def _part_drawing(module: Part, lift: int, colors: dict) -> dict:
    """Return a destroyable part's 3D drawing: its module `lift` cubes above the ship's middle plane, its weapons.

    It points the way the ship does (down the screen): its back on its first row.
    """
    half = max(abs(x) for x, _ in module.footprint)
    length = module.high[1] + 1
    cells = {(x + half, y, -(z + lift)): char for (x, y, z), char in module.cells.items()}
    drawing = layered_drawing(cells, 2 * half + 1, length, colors)
    weapons = numbered_weapons([(kind, x + half, y) for kind, x, y, _ in module.weapons])
    return {**drawing, "weapons": weapons} if weapons else drawing
