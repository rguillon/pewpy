"""The parts browser of the Dev menu: the catalog of built-in parts ships are made of, one part at a time.

It shows one kind of part (see pewpy.generators.models.parts.KINDS, picked in the Dev menu's Parts menu); Left
and Right go from one part to the next. Nothing is made nor saved: the parts are drawn in code. Independent from
rendering: the app shows `part_drawing`.
"""

from dataclasses import dataclass

from pewpy import config
from pewpy.generators.models.common.drawing import layered_drawing
from pewpy.generators.models.common.palette import GREYS, LIVERIES, PLAYER_TINT, Colors, palette
from pewpy.generators.models.parts import KINDS, MOUNTS, Part, of_kind

COLORS = Colors(PLAYER_TINT, "orange", LIVERIES[1])  # the parts' colors on show
FLAME_LENGTH = 6  # an engine's flame on show, in cubes
LEAST = 12 * config.MODEL_VOXEL  # the parts are drawn to the scale fitting at least this (world units)


def part_drawing(part: Part) -> dict:
    """Return a part as a 3D drawing, its front up the screen, its engines' flames going down."""
    left, front = part.low[0], part.high[1]
    width, length, _ = part.extent()
    cells = {(x - left, front - y, -z): char for (x, y, z), char in part.cells.items()}
    engines = [
        {"x": x - left, "y": front - y, "z": z, "width": flame, "length": FLAME_LENGTH, "towards": "bottom"}
        for x, y, z, flame in part.nozzles
    ]
    drawing = layered_drawing(cells, width, length, palette(GREYS, COLORS))
    return {**drawing, "engines": engines, "size": [width * config.MODEL_VOXEL, length * config.MODEL_VOXEL]}


@dataclass
class PartBrowser:
    """The kind of part on show (its index in KINDS) and the part of that kind."""

    kind_index: int = 0
    index: int = 0

    @property
    def kind(self) -> str:
        """Return the kind of part on show (see KINDS)."""
        return list(KINDS)[self.kind_index]

    @property
    def parts(self) -> list[Part]:
        """Return the parts of the kind on show."""
        return of_kind(self.kind)

    @property
    def part(self) -> Part:
        """Return the part on show."""
        return self.parts[self.index]

    def move(self, step: int) -> None:
        """Show the next part of the kind (step 1) or the previous one (-1), wrapping around."""
        self.index = (self.index + step) % len(self.parts)

    def size(self) -> tuple[float, float]:
        """Return the part's size, across and up the screen, in world units."""
        width, length, _ = self.part.extent()
        return width * config.MODEL_VOXEL, length * config.MODEL_VOXEL

    def title(self) -> str:
        """Return the part's name and its number among its kind's ("Bubble, small  (1/22)")."""
        return f"{self.part.name.capitalize()}  ({self.index + 1}/{len(self.parts)})"

    def details(self) -> str:
        """Return its kind, what it is, and how it mounts on a ship."""
        part = self.part
        where = MOUNTS[part.mount].split(":")[0]
        return f"{KINDS[self.kind]}. {part.description} Mounted {where}."

    def info(self) -> str:
        """Return its size in cubes, its weapons' and its engines' counts."""
        width, length, height = self.part.extent()
        found = [f"{width} x {length} x {height} cubes"]
        if self.part.weapons:
            found.append(f"{len(self.part.weapons)} weapon{'s' * (len(self.part.weapons) > 1)}")
        if self.part.nozzles:
            found.append(f"{len(self.part.nozzles)} nozzle{'s' * (len(self.part.nozzles) > 1)}")
        return "   ".join(found)
