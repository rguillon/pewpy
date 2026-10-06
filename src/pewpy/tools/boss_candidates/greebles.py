"""Surface details on a boss's core, once sculpted: breaking up the flat top of its hull.

A big core's hull rises from its outline to its full height a few cubes in, then stays flat. On that plateau:
- plating: the plateau cut in panels, some raised a cube (framed by the seams left round them), some sunk;
- machinery, scattered: blocks, grilled vents, small domes with a sensor, pipes with couplings, radiator fins,
  antennas on a base, rows of lights, lit trenches.
Only the hull's own plating gets them (not the decks, bridge, seams, sockets under the parts, wings or nozzles), so
the parts still stand where they were. A symmetric boss gets them on its left half, mirrored.
"""

import random
import zlib
from collections.abc import Callable

from pewpy.tools.boss_candidates.canvas import Canvas
from pewpy.tools.boss_candidates.sculpting import Cells

CORE_PLATING = "hHNLTk"  # a core column's top where details may go: its hull's plating and seams, its lower decks
PART_PLATING = "hHNtk"  # a part's: its plating, seams and housing
WING = "wW"  # a core's wings and sponsons: ribs and pods on them
Heights = dict[tuple[int, int], tuple[int, int]]


class Surface:
    """The core's cubes and heights, changed column by column (and the mirror column, on a symmetric boss)."""

    def __init__(self, cv: Canvas, cells: Cells, heights: Heights, symmetric: bool, level: int, plating: str) -> None:
        self.cv, self.cells, self.heights, self.symmetric, self.plating = cv, cells, heights, symmetric, plating
        last = (cv.w - 1) // 2 if symmetric else cv.w - 1
        self.plateau = {
            (x, y)
            for (x, y), (_, top) in heights.items()
            if x <= last and top >= level - 1 and cv.get(x, y) in plating and self.char(x, y) in plating
        }
        self.taken: set[tuple[int, int]] = set()
        self.deck = "t" if "t" in plating else "T"  # raised plates: a part's housing, or a core's lower decks

    def top(self, x: int, y: int) -> int:
        """Return a column's top."""
        return self.heights[x, y][1]

    def char(self, x: int, y: int) -> str:
        """Return a column's top cube."""
        return self.cells.get((x, y, -self.top(x, y)), ".")

    def free(self, cells: list[tuple[int, int]], margin: int = 1) -> bool:
        """Tell whether a footprint is all on the plateau's plating, away from other machinery."""
        return all(
            cell in self.plateau and self.char(*cell) in self.plating and cell not in self.taken for cell in cells
        ) and not any(
            (x + dx, y + dy) in self.taken
            for x, y in cells
            for dx in range(-margin, margin + 1)
            for dy in range(-margin, margin + 1)
        )

    def take(self, cells: list[tuple[int, int]]) -> None:
        """Keep other machinery off a footprint."""
        self.taken.update(cells)

    def raise_to(self, x: int, y: int, top: int, char: str, fill: str = "N") -> None:
        """Make a column (and its mirror) `top` high, `char` on top, `fill` under it down to its old top."""
        for column in self._columns(x):
            bottom, old = self.heights[column, y]
            for z in range(old + 1, top):
                self.cells[column, y, -z] = fill
            for z in range(top + 1, old + 1):
                self.cells.pop((column, y, -z), None)
            self.cells[column, y, -top] = char
            self.heights[column, y] = (bottom, max(bottom, top))

    def paint(self, x: int, y: int, char: str) -> None:
        """Paint a column's top cube (and its mirror's)."""
        for column in self._columns(x):
            self.cells[column, y, -self.heights[column, y][1]] = char

    def _columns(self, x: int) -> set[int]:
        return {x, self.cv.w - 1 - x} if self.symmetric else {x}


def greeble(cv: Canvas, cells: Cells, heights: Heights, symmetric: bool, level: int, *, part: bool = False) -> None:
    """Add plating and machinery on a core's plateau or a part's top (`level`: the hull's full height).

    A part gets smaller panels and only the small machinery. Drawn from the model's own plan, so the same model always
    gets the same details.
    """
    rng = random.Random(zlib.crc32("".join(cv.rows()).encode()))
    surface = Surface(cv, cells, heights, symmetric, level, PART_PLATING if part else CORE_PLATING)
    _plating(rng, surface, (3, 5) if part else (5, 9))
    spots = sorted(surface.plateau)
    machinery, weights = (PART_MACHINERY, PART_WEIGHTS) if part else (MACHINERY, WEIGHTS)
    for _ in range(len(spots) // 3):  # many tries: a footprint only fits where the plateau is wide enough
        x, y = rng.choice(spots)
        rng.choices(machinery, weights)[0](rng, surface, x, y)
    if not part:
        _wings(rng, cv, cells, heights, symmetric)


def _wings(rng: random.Random, cv: Canvas, cells: Cells, heights: Heights, symmetric: bool) -> None:
    """Break up the wings: ribs running along them from front to back, and weapon pods on them."""
    wings = {(x, y) for (x, y) in heights if cv.get(x, y) in WING}
    if not wings:
        return
    spacing = rng.randint(3, 5)
    surface = Surface(cv, cells, heights, symmetric, -99, WING)
    surface.plateau = {(x, y) for x, y in surface.plateau if (x, y) in wings}
    for x, y in sorted(surface.plateau):
        if x % spacing == 0:
            surface.raise_to(x, y, surface.top(x, y) + 1, "W", fill="w")
    spots = sorted(surface.plateau)
    for _ in range(len(spots) // 40):
        _pod(rng, surface, *rng.choice(spots))


def _pod(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Put a weapon pod on a wing: a long block, a barrel or a glowing tip at its front (towards the nose)."""
    long = rng.randint(4, 7)
    cells = [(x, y + i) for i in range(long)] + [(x + 1, y + i) for i in range(long)]
    if not s.free(cells, margin=0):
        return
    base = max(s.top(*cell) for cell in cells)
    for cx, cy in cells:
        s.raise_to(cx, cy, base + 2, "N" if (cy - y) % 3 else "k", fill="N")
    tip = y + long
    if (x, tip) in s.heights:
        s.raise_to(x, tip, base + 2, rng.choice("rp"), fill="N")
    s.take(cells)


def _plating(rng: random.Random, s: Surface, sizes: tuple[int, int]) -> None:
    """Cut the plateau in panels: some raised a cube inside a seam, some sunk."""
    size = rng.randint(*sizes)
    ox, oy = rng.randrange(size), rng.randrange(size)
    panels: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for x, y in s.plateau:
        gx, gy = (x + ox) // size, (y + oy) // size
        if (x + ox) % size and (y + oy) % size:  # the panel's first row and column stay: its seam
            panels.setdefault((gx, gy), []).append((x, y))
    for cells in panels.values():
        roll = rng.random()
        if roll < 0.35:
            char = rng.choice("HH" + s.deck)
            for x, y in cells:
                s.raise_to(x, y, s.top(x, y) + 1, char)
        elif roll < 0.5:
            for x, y in cells:
                s.raise_to(x, y, s.top(x, y) - 1, "k")


def _box(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Put a block of machinery, maybe a light on its corner."""
    wide, long = rng.randint(2, 4), rng.randint(2, 5)
    cells = [(x + dx, y + dy) for dx in range(wide) for dy in range(long)]
    if not s.free(cells):
        return
    top = max(s.top(*cell) for cell in cells) + rng.randint(1, 3)
    char = rng.choice(s.deck + "S")
    for cx, cy in cells:
        s.raise_to(cx, cy, top, char)
    if rng.random() < 0.4:
        s.paint(x, y, "p")
    s.take(cells)


def _vent(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Sink a grilled vent: sunk a cube, dark slats across it."""
    wide, long = rng.randint(2, 4), rng.randint(3, 6)
    cells = [(x + dx, y + dy) for dx in range(wide) for dy in range(long)]
    if not s.free(cells):
        return
    for cx, cy in cells:
        s.raise_to(cx, cy, s.top(cx, cy) - 1, "k" if (cy - y) % 2 else "r")
    s.take(cells)


def _dome(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Put a small dome, a sensor on top."""
    r = rng.randint(1, 2)
    cells = [(x + dx, y + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r + 1]
    if not s.free(cells):
        return
    base = max(s.top(*cell) for cell in cells)
    for cx, cy in cells:
        rise = r + 1 - max(abs(cx - x), abs(cy - y))
        s.raise_to(cx, cy, base + rise, "S")
    if rng.random() < 0.5:
        s.paint(x, y, "R")
    s.take(cells)


def _pipe(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Run a pipe along the hull, couplings every few cubes, a pump at each end."""
    long = rng.randint(6, 14)
    along_y = rng.random() < 0.7
    cells = [(x, y + i) if along_y else (x + i, y) for i in range(long)]
    if not s.free(cells, margin=0):
        return
    for i, (cx, cy) in enumerate(cells):
        end = i in (0, long - 1)
        s.raise_to(cx, cy, s.top(cx, cy) + (2 if end else 1), "N" if end else ("k" if i % 4 == 0 else "H"))
    s.take(cells)


def _radiator(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Put radiator fins: thin ridges side by side."""
    fins, long = rng.randint(3, 5), rng.randint(3, 6)
    cells = [(x + 2 * i, y + j) for i in range(fins) for j in range(long)]
    gaps = [(x + 2 * i + 1, y + j) for i in range(fins - 1) for j in range(long)]
    if not s.free(cells + gaps):
        return
    for cx, cy in cells:
        s.raise_to(cx, cy, s.top(cx, cy) + 2, "W")
    s.take(cells + gaps)


def _antenna(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Put an antenna on a base, a light on its tip."""
    base = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
    if not s.free(base):
        return
    low = max(s.top(*cell) for cell in base) + 1
    for cx, cy in base:
        s.raise_to(cx, cy, low, "N")
    s.raise_to(x, y, low + rng.randint(2, 5), rng.choice("Rp"), fill="k")
    s.take(base)


def _lights(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Put a row of lights along the hull."""
    cells = [(x, y + 2 * i) for i in range(rng.randint(3, 6))]
    if not s.free(cells, margin=0):
        return
    for cx, cy in cells:
        s.paint(cx, cy, "p")
    s.take(cells)


def _trench(rng: random.Random, s: Surface, x: int, y: int) -> None:
    """Sink a trench along the hull, lit along its floor."""
    wide, long = rng.randint(1, 2), rng.randint(8, 16)
    cells = [(x + dx, y + dy) for dx in range(wide) for dy in range(long)]
    if not s.free(cells):
        return
    light = rng.choice("pg")
    for cx, cy in cells:
        s.raise_to(cx, cy, s.top(cx, cy) - 2, light if (cy - y) % 3 == 0 else "r")
    s.take(cells)


MACHINERY: list[Callable[[random.Random, Surface, int, int], None]] = [
    _box,
    _vent,
    _dome,
    _pipe,
    _radiator,
    _antenna,
    _lights,
    _trench,
]
WEIGHTS = [5, 3, 2, 3, 2, 2, 2, 1]
PART_MACHINERY: list[Callable[[random.Random, Surface, int, int], None]] = [_box, _vent, _lights, _pipe]
PART_WEIGHTS = [3, 3, 2, 1]
