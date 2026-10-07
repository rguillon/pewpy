"""A built-in part being drawn: its cubes, its weapons' barrel tips and its engines' nozzles."""

from dataclasses import dataclass, field

Cell = tuple[int, int, int]  # x across (0 its middle), y from its back (0) towards the front, z up (0 its lowest cubes)
Weapon = tuple[str, int, int, int]  # (kind, x, y, z) of a barrel's tip, where its shots come out
Nozzle = tuple[int, int, float, float]  # (x, y, z, width): an engine's nozzle on its back face, its flame going back


@dataclass
class Piece:
    """A small 3D piece of machinery, symmetric across its middle (x = 0), sitting on z = 0.

    Its cubes are palette characters (see pewpy.generators.models.common.palette): N dark plates, h hull, H lighter
    bands, S raised tops and domes, k dark lines, r barrels, W light edges and fins, o nozzles, p markings and lights,
    G and R glowing cores and sensors.
    """

    cells: dict[Cell, str] = field(default_factory=dict)
    weapons: list[Weapon] = field(default_factory=list)
    nozzles: list[Nozzle] = field(default_factory=list)

    def box(self, x0: int, x1: int, y0: int, y1: int, z0: int, z1: int, char: str) -> None:
        """Fill a box (bounds included) and its mirror image across x = 0."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.cells[x, y, z] = self.cells[-x, y, z] = char

    def housing(self, half: int, y0: int, y1: int, z0: int, z1: int) -> None:
        """Fill a housing `half` cubes each side of the middle: dark sides, its top plated.

        The top's rim lighter, seams across it every few rows, a light in its front corners.
        """
        self.box(-half, half, y0, y1, z0, z1, "N")
        self.box(-half, half, y0, y1, z1, z1, "H")
        if half > 0:
            self.box(-half + 1, half - 1, y0 + 1, y1 - 1, z1, z1, "h")
        for y in range(y0 + 2, y1 - 1, 3):
            self.box(-half + 1, half - 1, y, y, z1, z1, "k")
        self.box(half, half, y1, y1, z1, z1, "p")

    def disc(self, y: int, radius: float, z0: int, z1: int, char: str) -> None:
        """Fill an upright cylinder around (0, y): a round footprint."""
        reach = int(radius)
        for dx in range(-reach, reach + 1):
            for dy in range(-reach, reach + 1):
                if dx * dx + dy * dy <= radius * radius + radius * 0.8:
                    self.box(dx, dx, y + dy, y + dy, z0, z1, char)

    def weapon(self, kind: str, x: int, y: int, z: int) -> None:
        """Add a weapon whose barrel's tip is at (x, y, z), and its mirror image."""
        self.weapons += [(kind, column, y, z) for column in sorted({x, -x})]

    def footprint(self) -> set[tuple[int, int]]:
        """Return the cells it stands on, seen from above."""
        return {(x, y) for x, y, _ in self.cells}

    def height(self) -> int:
        """Return how many cubes high it is."""
        return max(z for _, _, z in self.cells) + 1
