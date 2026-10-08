"""A model being assembled around its middle, with slots where parts can be placed.

A Frame is the model-in-progress: its cells (cubes placed so far), its slots (where parts may be stamped),
and its constraints. Both ships and bosses are built the same way: start with a frame, stamp parts into slots,
then make a drawing.

Both players, enemies and bosses use the same Frame + Part system, so they share the same library and the same
placement engine.
"""

from collections import deque
from dataclasses import dataclass, field

from pewpy.generators.models.common.drawing import layered_drawing
from pewpy.generators.models.library.part import Cell, Part


@dataclass
class Slot:
    """A place on a frame another part may be stamped: where, which way it faces, how big it may be."""

    name: str
    at: Cell  # (x, y, z) where the part's anchor goes
    face: str  # "up", "down", "out", "forward": which way barrels point
    capacity: int  # the part's half-width must be <= this


@dataclass
class Frame:
    """A model being assembled: its cells so far, and where parts may be stamped.

    The frame's origin is at its middle column (x = 0). Row 0 is its back; row indices increase towards the
    nose. Layer 0 is its bottom; layer indices go up towards the camera.
    """

    cells: dict[Cell, str] = field(default_factory=dict)
    slots: dict[str, Slot] = field(default_factory=dict)
    constraints: dict[str, object] = field(default_factory=dict)

    # ---- Helpers ----

    def empty_cells(self) -> list[Cell]:
        """Return all empty cells within the current bounds."""
        if not self.cells:
            return []
        xs = [c[0] for c in self.cells]
        ys = [c[1] for c in self.cells]
        zs = [c[2] for c in self.cells]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        cells_set = set(self.cells)
        return [
            (x, y, z)
            for x in range(min_x - 1, max_x + 2)
            for y in range(min_y - 1, max_y + 2)
            for z in range(min_z - 1, max_z + 2)
            if (x, y, z) not in cells_set
        ]

    def put(self, x: int, y: int, z: int, char: str) -> None:
        """Set a cube at (x, y, z). Mirroring is handled by the caller (stamp_part)."""
        self.cells[(x, y, z)] = char

    def mirror_cell(self, cell: Cell) -> Cell:
        """Return the mirror image across the middle column."""
        x, y, z = cell
        return (-x, y, z)

    # ---- One-piece constraint (VSL-4) ----

    def is_one_piece(self) -> bool:
        """Tell whether all cubes are connected through faces."""
        if not self.cells:
            return True
        start = min(self.cells)
        visited = {start}
        todo = deque([start])
        while todo:
            cell = todo.popleft()
            x, y, z = cell
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                neighbour = (x + dx, y + dy, z + dz)
                if neighbour in self.cells and neighbour not in visited:
                    visited.add(neighbour)
                    todo.append(neighbour)
        return len(visited) == len(self.cells)

    # ---- Stamping a part ----

    def stamp_part(self, part: Part, slot_name: str) -> bool:
        """Stamp a part into a slot.

        Return True when it fits (no overlap with existing cells, and within bounds).
        """
        slot = self.slots.get(slot_name)
        if slot is None:
            return False

        x0, y0, z0 = slot.at
        capacity = slot.capacity

        if part.half() > capacity:
            return False

        added: set[Cell] = set()

        for (px, py, pz), char in part.cells.items():
            # Place the part cell; mirroring is handled by Part.put already
            target_x = x0 + px
            target_y = y0 + py
            target_z = z0 + pz

            # Part.put already mirrors across x=0, so we just add at the target
            if (target_x, target_y, target_z) in added:
                continue
            if (target_x, target_y, target_z) in self.cells:
                return False  # overlap
            # Mirror: if the part cell has negative x, its mirror goes positive and vice versa
            # But Part.put already handled mirroring, so we just store what we placed
            self.cells[(target_x, target_y, target_z)] = char
            added.add((target_x, target_y, target_z))

        # Weapons are already signed for mirroring in the part
        for _kind, wx, wy, wz in part.weapons:
            self.cells[(x0 + wx, y0 + wy, z0 + wz)] = "r"

        # Nozzles
        for nx, ny, nz, _width in part.nozzles:
            self.cells[(x0 + nx, y0 + ny, int(z0 + nz))] = "o"

        return True

    # ---- Getting a drawing ----

    def drawing(self, colors: dict) -> dict:
        """Return this frame as a 3D drawing."""
        return layered_drawing(self.cells, self.span(), self.length(), colors)

    # ---- Bounds ----

    def span(self) -> int:
        """Return how many cubes across it is."""
        if not self.cells:
            return 1
        xs = [c[0] for c in self.cells]
        return max(xs) - min(xs) + 1

    def length(self) -> int:
        """Return how many cubes long it is."""
        if not self.cells:
            return 1
        ys = [c[1] for c in self.cells]
        return max(ys) - min(ys) + 1

    def height(self) -> int:
        """Return how many cubes high it is."""
        if not self.cells:
            return 1
        zs = [c[2] for c in self.cells]
        return max(zs) - min(zs) + 1
