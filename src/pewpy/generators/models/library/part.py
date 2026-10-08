"""A prebuilt piece of geometry: its cubes, its weapons' barrel tips, its engines' nozzles, and what it is.

Every part of the library (see pewpy.generators.models.library) is a function `(rng, size) -> Part`: `size` 1 for a
ship's, more on a boss or as one of a boss's destroyable parts. A part is built around its own middle (`x = 0`, so
drawing right also draws left), its back on row 0, its lowest cubes on `z = 0`, then stamped on a frame at some slot
(see pewpy.generators.models.assembly.slots).

Its cubes are palette characters (see pewpy.generators.models.common.palette). Parts use the characters every palette
has, so the same part can go on a ship and on a boss:

    N heavy plates, h hull, H lighter bands, S raised tops and domes, k dark lines and seams, r barrels and recesses,
    w plating, W light edges and fins, o nozzles, t containers, p markings and lights, G and R glowing cores and
    sensors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

Cell = tuple[int, int, int]  # x across (0 its middle), y from its back (0) towards the front, z up (0 its lowest cubes)
Weapon = tuple[str, int, int, int]  # (kind, x, y, z) of a barrel's tip, where its shots come out
Nozzle = tuple[int, int, float, float]  # (x, y, z, width): an engine's nozzle on its back face, its flame going back
Tags = frozenset[str]  # what a part is, to match it to a slot (see assembly.slots)

# What a part is. A part may be several things (a missile rack is a "weapon" and a "pod").
HULL = "hull"
WING = "wing"
BOOM = "boom"
ENGINE = "engine"
WEAPON = "weapon"
GUN = "gun"
MISSILE = "missile"
COCKPIT = "cockpit"
SENSOR = "sensor"
POWER = "power"
VENT = "vent"
STORES = "stores"
PLATING = "plating"
PART = "part"  # a boss's destroyable part
PAINT = "paint"  # a livery or a marking: not geometry on its own, it recolours what is there


@dataclass
class Part:
    """A piece of geometry: its cubes, its weapons' barrel tips, its engines' nozzles, and its tags.

    Built around its middle (`x = 0`, so drawing right also draws left), sitting on `z = 0`, its back on row 0. The
    drawing methods mirror across the middle; the transforms (`moved`, `turned`, `hung`, `rolled`, `grown`) put it on a
    frame (see pewpy.generators.models.assembly.frame).
    """

    cells: dict[Cell, str] = field(default_factory=dict)
    weapons: list[Weapon] = field(default_factory=list)
    nozzles: list[Nozzle] = field(default_factory=list)
    tags: Tags = frozenset()

    # ---- Drawing ----

    def put(self, x: int, y: int, z: int, char: str) -> None:
        """Set a cube (and its mirror image across the middle)."""
        self.cells[x, y, z] = self.cells[-x, y, z] = char

    def box(self, x0: int, x1: int, y0: int, y1: int, z0: int, z1: int, char: str) -> None:
        """Fill a box (bounds included) and its mirror image across the middle."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z1, z1) + 1):
                    self.put(x, y, z, char)

    def slab(self, half: int, y0: int, y1: int, z0: int, z1: int, char: str, section: str = "flat") -> None:
        """Fill a slab `half` cubes each side of the middle, its cross-section flat/cut/round."""
        width = max(1, half)
        for x in range(-width, width + 1):
            reach = abs(x) / (width + 0.4)
            if section == "round" and reach > 1.0:
                continue
            for y in range(min(y0, y1), max(y0, y1) + 1):
                if section == "round":
                    shrink = (1.0 - reach * reach) ** 0.5
                    top, bottom = round(z1 * shrink), round(z0 * shrink)
                elif section == "cut" and abs(x) == width:
                    top, bottom = z1 - 1, z0 + 1
                else:
                    top, bottom = z1, z0
                for z in range(bottom, top + 1):
                    self.put(x, y, z, char)

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

    def dome(self, y: int, radius: float, z: int, char: str) -> None:
        """Fill a half sphere standing on (0, y, z): a sensor dome, a radome, a blister."""
        for step in range(int(radius) + 1):
            r = (radius * radius - step * step) ** 0.5
            self.disc(y, r, z + step, z + step, char)

    def tube(self, radius: float, y0: int, y1: int, z: int, char: str) -> None:
        """Fill a cylinder lying along the hull (its axis at `z`): a pipe, a tank, a boom."""
        reach = int(radius)
        for dx in range(-reach, reach + 1):
            for dz in range(-reach, reach + 1):
                if dx * dx + dz * dz <= radius * radius + 0.5:
                    self.box(dx, dx, y0, y1, z + dz, z + dz, char)

    def barrel(self, x: int, y0: int, y1: int, z: int, radius: int = 0, char: str = "r") -> None:
        """Draw a barrel along the hull (its axis at (x, z)), `radius` cubes thick, from row y0 to y1."""
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if dx * dx + dz * dz <= radius * radius + radius * 0.8:
                    self.box(x + dx, x + dx, y0, y1, z + dz, z + dz, char)

    # ---- Weapons ----

    def weapon(self, kind: str, x: int, y: int, z: int) -> None:
        """Add a weapon whose barrel's tip is at (x, y, z), and its mirror image."""
        self.weapons += [(kind, column, y, z) for column in sorted({x, -x})]

    def nozzle(self, x: int, y: int, z: float, width: float) -> None:
        """Add an engine's nozzle on its back face (at (x, y, z)), its flame going back, `width` cubes wide."""
        self.nozzles.append((x, y, z, width))

    def fires(self, kind: str, tip: Cell) -> None:
        """Add a weapon of a kind whose barrel's tip is at `tip`, marking the cube so the barrel never ends in air."""
        self.weapon(kind, *tip)

    # ---- Measuring ----

    def footprint(self) -> set[tuple[int, int]]:
        """Return the cells it stands on, seen from above."""
        return {(x, y) for x, y, _ in self.cells}

    def base(self) -> set[tuple[int, int]]:
        """Return the cells on its lowest layer (`z = 0`)."""
        return {(x, y) for x, y, z in self.cells if z == 0}

    def half(self) -> int:
        """Return how many cubes from its middle its widest row reaches."""
        return max((abs(x) for x, _, _ in self.cells), default=0)

    def height(self) -> int:
        """Return how many cubes high it is."""
        return max(z for _, _, z in self.cells) + 1

    def length(self) -> int:
        """Return how many cubes long it is."""
        return max(y for _, y, _ in self.cells) + 1

    def span(self) -> int:
        """Return how many cubes across it is."""
        return 2 * self.half() + 1

    def middle(self) -> int:
        """Return its middle row (its rows from its back, 0)."""
        return max(y for _, y in self.footprint()) // 2

    def volume(self) -> int:
        """Return how many cubes it is made of."""
        return len(self.cells)

    def column(self, x: int, y: int) -> list[int]:
        """Return the heights of its cubes at (x, y), lowest first (empty where it has none)."""
        return sorted(z for cx, cy, z in self.cells if (cx, cy) == (x, y))

    # ---- Transforms. A part keeps its tags through all of them. ----

    def moved(self, x: int, y: int, z: int) -> Part:
        """Return the same part moved by (x, y, z)."""
        return self._moved(lambda px, py, pz: (px + x, py + y, pz + z))

    def turned(self) -> Part:
        """Return the same part with its back to the front (barrels the other way)."""
        far = self.length() - 1
        return self._moved(lambda x, y, z: (x, far - y, z))

    def hung(self) -> Part:
        """Return the same part upside down (top becomes base)."""
        tall = self.height() - 1
        return self._moved(lambda x, y, z: (x, y, tall - z))

    def rolled(self) -> Part:
        """Return the same part on its side (base facing right)."""
        tall = self.height() - 1
        return self._moved(lambda x, y, z: (tall - z, y, x))

    def grown(self, times: int = 1) -> Part:
        """Return the same part `times` times bigger: each cube becomes a `times` cube block.

        Its weapons and nozzles come along, so a gun stamped on a big part still fires from its barrels' tips.
        """
        if times < 1:
            msg = "a part grows, it never shrinks"
            raise ValueError(msg)
        cells: dict[Cell, str] = {}
        for (x, y, z), char in self.cells.items():
            for dx in range(-times // 2, times - times // 2):
                for dy in range(times):
                    for dz in range(times):
                        cells[x * times + dx, y * times + dy, z * times + dz] = char
        return Part(
            cells,
            [(kind, x * times, y * times, z * times) for kind, x, y, z in self.weapons],
            [(x * times, y * times, z * times, width * times) for x, y, z, width in self.nozzles],
            self.tags,
        )

    def _moved(self, move: Callable[[int, int, int], tuple[int, int, int]]) -> Part:
        """Return a copy with every cube, weapon and nozzle put through `move`."""
        return Part(
            {move(x, y, z): char for (x, y, z), char in self.cells.items()},
            [(kind, *move(x, y, z)) for kind, x, y, z in self.weapons],
            [(*move(x, y, z), width) for x, y, z, width in self.nozzles],
            self.tags,
        )

    # ---- Editing ----

    def tagged(self, *tags: str) -> Part:
        """Return the same part with more tags."""
        return Part(self.cells, self.weapons, self.nozzles, self.tags | frozenset(tags))

    def cut(self, chars: str) -> Part:
        """Return the same part without its cubes of any of `chars`, and what they carried."""
        if not self.cells:
            return self
        dropped = {cell for cell, char in self.cells.items() if char in chars}
        return Part(
            {cell: char for cell, char in self.cells.items() if cell not in dropped},
            [weapon for weapon in self.weapons if (weapon[1], weapon[2], weapon[3]) not in dropped],
            [nozzle for nozzle in self.nozzles if (nozzle[0], nozzle[1], round(nozzle[2])) not in dropped],
            self.tags,
        )

    def painted(self, chars: str, with_char: str) -> Part:
        """Return the same part with its cubes of any of `chars` painted `with_char`."""
        return Part(
            {cell: (with_char if char in chars else char) for cell, char in self.cells.items()},
            self.weapons,
            self.nozzles,
            self.tags,
        )

    # ---- Combining ----

    def __or__(self, other: Part) -> Part:
        """Return both parts together, the other one's cubes over this one's."""
        return Part(
            self.cells | other.cells,
            self.weapons + other.weapons,
            self.nozzles + other.nozzles,
            self.tags | other.tags,
        )

    def __len__(self) -> int:
        """Return how many cubes it is made of."""
        return len(self.cells)

    def __bool__(self) -> bool:
        """Tell whether it has any cube."""
        return bool(self.cells)

    def __iter__(self) -> Iterator[Cell]:
        """Iterate over its cubes."""
        return iter(self.cells)
