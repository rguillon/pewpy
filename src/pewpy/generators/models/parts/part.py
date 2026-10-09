"""A built-in part of the catalog: its cubes, how it mounts on a ship, its weapons' barrel tips and engines' nozzles.

A part is drawn once, in its own cubes, by a `Sketch`, and never changes: the ship maker places it as it is (see
pewpy.generators.models.ships.placing). Its cubes are palette characters (see models.common.palette).
"""

from dataclasses import dataclass, field
from functools import cached_property

Cell = tuple[int, int, int]  # x across, y along the ship (towards the nose), z up (towards the camera)
Weapon = tuple[str, int, int, int]  # (kind, x, y, z) of a barrel's tip, where its shots come out
Nozzle = tuple[float, int, float, float]  # (x, y, z, width): an engine's nozzle on its back face, its flame going back

# How a part mounts (before the colon), and where its own cubes are (its origin):
MOUNTS = {
    "hull": "as the ship's body: its axis on x = 0, its tail on y = 0, its middle plane on z = 0",
    "wing": "on the hull's side: a left wing, its root on x = 0, its root's trailing edge on y = 0, its root on z = 0",
    "top": "on top of the ship: its middle on x = 0, its back on y = 0, its bottom on z = 0",
    "nose": "on the front: its middle on x = 0, its back on y = 0, its barrel's or its axis's height on z = 0",
    "tail": "on the back: its middle on x = 0, its nozzle on y = 0, its axis on z = 0",
    "pod": "beside the hull, under a wing or on its tip: its axis on x = 0 and z = 0, its back on y = 0",
    "under": "under a wing or the hull: its middle on x = 0, its back on y = 0, its top on z = 0",
    "side": "on the hull's side: drawn for the left, its inner face on x = 0, its back on y = 0, its middle on z = 0",
    "tip": "on a wing's tip: its middle on x = 0, its back on y = 0, its middle on z = 0",
}


@dataclass(frozen=True)
class Part:
    """A built-in part: what it is, how it mounts (see MOUNTS), its cubes, weapons and nozzles."""

    name: str
    kind: str  # its family in the catalog: "hull", "wing", "gun"... (see catalog.KINDS)
    mount: str
    description: str
    cells: dict[Cell, str]
    weapons: tuple[Weapon, ...] = ()
    nozzles: tuple[Nozzle, ...] = ()

    @cached_property
    def low(self) -> Cell:
        """Return its lowest x, y and z."""
        xs, ys, zs = zip(*self.cells, strict=True)
        return min(xs), min(ys), min(zs)

    @cached_property
    def high(self) -> Cell:
        """Return its highest x, y and z."""
        xs, ys, zs = zip(*self.cells, strict=True)
        return max(xs), max(ys), max(zs)

    def extent(self) -> Cell:
        """Return how many cubes it covers across, along and up."""
        (x0, y0, z0), (x1, y1, z1) = self.low, self.high
        return x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1

    @cached_property
    def symmetric(self) -> bool:
        """Tell whether it's its own mirror image across x = 0 (its cubes' places)."""
        return all((-x, y, z) in self.cells for x, y, z in self.cells)

    @cached_property
    def footprint(self) -> frozenset[tuple[int, int]]:
        """Return the (x, y) it covers, seen from above."""
        return frozenset((x, y) for x, y, _ in self.cells)

    @cached_property
    def rows(self) -> dict[int, tuple[int, int, int]]:
        """Return, for each y, its half width on x = 0's side and its top and bottom (a hull's profile)."""
        found: dict[int, tuple[int, int, int]] = {}
        for x, y, z in self.cells:
            half, top, bottom = found.get(y, (0, z, z))
            found[y] = (max(half, abs(x)), max(top, z), min(bottom, z))
        return found


@dataclass
class Sketch:
    """A part being drawn: cubes put one by one or in boxes, mirrored across x = 0 or not."""

    cells: dict[Cell, str] = field(default_factory=dict)
    weapons: list[Weapon] = field(default_factory=list)
    nozzles: list[Nozzle] = field(default_factory=list)

    def put(self, x: int, y: int, z: int, char: str, *, mirror: bool = True) -> None:
        """Set a cube (and its mirror image)."""
        self.cells[x, y, z] = char
        if mirror:
            self.cells[-x, y, z] = char

    def box(self, x0: int, x1: int, y0: int, y1: int, z0: int, z1: int, char: str, *, mirror: bool = True) -> None:
        """Fill a box, its bounds included (and its mirror image)."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, char, mirror=mirror)

    def rod(self, y0: int, y1: int, radius: float, char: str, z: float = 0.0, x: float = 0.0) -> None:
        """Fill a round rod along y, around (x, z), from y0 to y1 (and its mirror image when off the middle)."""
        reach = int(radius + 0.5)
        for dx in range(-reach, reach + 1):
            for dz in range(-reach, reach + 1):
                if dx * dx + dz * dz <= radius * radius + 0.25:
                    self.box(round(x + dx), round(x + dx), y0, y1, round(z + dz), round(z + dz), char, mirror=x != 0)

    def disc(self, y: int, radius: float, z0: int, z1: int, char: str) -> None:
        """Fill an upright cylinder around (0, y): a round footprint."""
        reach = int(radius)
        for dx in range(-reach, reach + 1):
            for dy in range(-reach, reach + 1):
                if dx * dx + dy * dy <= radius * radius + radius * 0.8:
                    self.box(dx, dx, y + dy, y + dy, z0, z1, char, mirror=False)

    def housing(self, half: int, y0: int, y1: int, z0: int, z1: int) -> None:
        """Fill a plated housing `half` cubes each side of the middle.

        Dark sides, a lighter rim, seams across its top, a light in its front corners.
        """
        self.box(-half, half, y0, y1, z0, z1, "N")
        self.box(-half, half, y0, y1, z1, z1, "H")
        if half > 0:
            self.box(-half + 1, half - 1, y0 + 1, y1 - 1, z1, z1, "h")
        for y in range(y0 + 2, y1 - 1, 3):
            self.box(-half + 1, half - 1, y, y, z1, z1, "k")
        self.box(half, half, y1, y1, z1, z1, "p")

    def weapon(self, kind: str, x: int, y: int, z: int, *, mirror: bool = True) -> None:
        """Add a weapon whose barrel's tip is at (x, y, z) (and its mirror image)."""
        self.weapons += [(kind, column, y, z) for column in sorted({x, -x} if mirror else {x})]

    def nozzle(self, x: float, y: int, z: float, width: float, *, mirror: bool = True) -> None:
        """Add an engine's nozzle (and its mirror image)."""
        self.nozzles += [(column, y, z, width) for column in sorted({x, -x} if mirror else {x})]

    def part(self, name: str, kind: str, mount: str, description: str) -> Part:
        """Return the part drawn."""
        return Part(name, kind, mount, description, dict(self.cells), tuple(self.weapons), tuple(self.nozzles))
