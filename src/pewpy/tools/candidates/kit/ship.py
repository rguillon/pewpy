"""A ship being assembled from parts: its voxels, its engines' nozzles, its weapons, written as a 3D drawing."""

from dataclasses import dataclass, field

from pewpy.tools.common.drawing import layered_drawing, numbered_weapons

PLAYER_SCALE = 2  # a player's ship is drawn this much finer than the enemies (see pewpy.graphics.models: "scale")
Cell = tuple[int, int, int]  # x across (0 on the ship's axis), y along it (0 at the tail), z up (towards the camera)


@dataclass
class Nozzle:
    """Where an engine's flame comes out: the middle of its nozzle's back face, and how wide the flame is."""

    x: float
    y: int
    z: float
    width: float


@dataclass
class Weapon:
    """A weapon: what it is (see layers.WEAPON_KINDS) and its barrel's tip, where its shots come out."""

    kind: str
    x: int
    y: int
    z: int


@dataclass
class Ship:
    """The voxels placed so far, each a palette character (see pewpy.tools.common.palette), and the engines' nozzles.

    Parts are placed on the left half (x <= 0) and mirrored to the right unless `mirror=False`: a ship with any
    unmirrored part is lopsided.
    """

    cells: dict[Cell, str] = field(default_factory=dict)
    nozzles: list[Nozzle] = field(default_factory=list)
    weapons: list[Weapon] = field(default_factory=list)
    symmetric: bool = True

    def put(self, x: int, y: int, z: int, char: str, *, mirror: bool = True, over: bool = True) -> None:
        """Set a voxel (and its mirror image); `over=False` keeps what's there."""
        for column in {x, -x} if mirror else {x}:
            if over or (column, y, z) not in self.cells:
                self.cells[column, y, z] = char
        if not mirror and x != 0:
            self.symmetric = False

    def box(self, x0: int, x1: int, y0: int, y1: int, z0: int, z1: int, char: str, *, mirror: bool = True) -> None:
        """Fill a box, its bounds included."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, char, mirror=mirror)

    def get(self, x: int, y: int, z: int) -> str | None:
        """Return the voxel there, if any."""
        return self.cells.get((x, y, z))

    def tops(self) -> dict[tuple[int, int], int]:
        """Return the highest voxel's z at each (x, y)."""
        highest: dict[tuple[int, int], int] = {}
        for x, y, z in self.cells:
            highest[x, y] = max(z, highest.get((x, y), z))
        return highest

    def nozzle(self, x: float, y: int, z: float, width: float, *, mirror: bool = True) -> None:
        """Add an engine's nozzle (and its mirror image)."""
        self.nozzles.append(Nozzle(x, y, z, width))
        if mirror and x != 0:
            self.nozzles.append(Nozzle(-x, y, z, width))
        if not mirror and x != 0:
            self.symmetric = False

    def weapon(self, kind: str, x: int, y: int, z: int, *, mirror: bool = True) -> None:
        """Add a weapon (and its mirror image) whose barrel's tip is at (x, y, z)."""
        for column in {x, -x} if mirror else {x}:
            self.weapons.append(Weapon(kind, column, y, z))

    def size(self) -> tuple[int, int]:
        """Return how many columns and rows the ship covers."""
        xs = [x for x, _, _ in self.cells]
        ys = [y for _, y, _ in self.cells]
        return max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

    def plan(self) -> list[str]:
        """Return the ship seen from above: each column's highest voxel, row 0 at the tail (as drawings are)."""
        left, back = self._origin()
        width, length = self.size()
        highest: dict[tuple[int, int], tuple[int, str]] = {}
        for (x, y, z), char in self.cells.items():
            key = (x - left, y - back)
            if key not in highest or z > highest[key][0]:
                highest[key] = (z, char)
        return ["".join(highest.get((x, y), (0, "."))[1] for x in range(width)) for y in range(length)]

    def drawing(self, colors: dict, flame_length: int, *, player: bool = False) -> dict:
        """Return the ship as a 3D drawing: its layers, palette, engines (flames out of its tail), weapons (numbered).

        An enemy points down the screen: its tail on the drawing's first row, its flames "towards" the top. A player's
        ship (`player`) points up: its tail on the last row, its flames towards the bottom; it's drawn finer
        (PLAYER_SCALE cubes per model cube, like the game's ships) and lists no weapons (the player's guns don't use
        them).
        Engines whose flame would run through the ship are left out.
        """
        left, back = self._origin()
        width, length = self.size()

        def row(y: float) -> float:  # the drawing's row of a y from the tail
            return length - 1 - (y - back) if player else y - back

        cells = {(x - left, round(row(y)), -z): char for (x, y, z), char in self.cells.items()}  # layers: up is < 0
        engines = []
        for nozzle in self.nozzles:
            behind = any((round(nozzle.x), y, round(nozzle.z)) in self.cells for y in range(min(self._ys()), nozzle.y))
            if behind:
                continue
            engine = {
                "x": nozzle.x - left,
                "y": row(nozzle.y),
                "width": nozzle.width,
                "length": flame_length,
                "towards": "bottom" if player else "top",
            }
            if nozzle.z:
                engine["z"] = nozzle.z
            engines.append(engine)
        drawing = {**layered_drawing(cells, width, length, colors), "engines": engines}
        if player:
            return {"scale": PLAYER_SCALE, **drawing}
        weapons = numbered_weapons([(weapon.kind, weapon.x - left, weapon.y - back) for weapon in self.weapons])
        return {**drawing, "weapons": weapons}

    def _ys(self) -> list[int]:
        return [y for _, y, _ in self.cells]

    def _origin(self) -> tuple[int, int]:
        return min(x for x, _, _ in self.cells), min(self._ys())
