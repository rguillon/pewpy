"""Turn a candidate's plan (a drawing seen from above, see canvas.py) into a real 3D model.

The plan says what each cell is (by its character); `Shaping` says what each character is in 3D (its role) and how
big things get. Heights are in cubes, z up towards the camera (0 on the model's middle plane):
- hull: a body whose height grows with the distance to its outline (`slope` cubes a cube inwards), so its edges are
  chamfered and its middle is the thickest; the top rises higher than the underside goes down (ships are flat
  underneath), whose lowest cubes are darker;
- raised (with a tier, 1 and up): stacked on the hull, each tier on the one below, chamfered the same way (spines,
  decks, bridges, cockpits, sensors);
- seam: hull, but its top cube is missing (panel lines, hangar bays: recessed);
- wing: a thin plate rising a little towards its tip (dihedral), thicker at its root;
- pod: a rounded block of its own, around the middle plane (turrets, containers);
- gun: a thin barrel, at height `gun`.
A raised cell's color is only on its top; below it, the hull's (`fill`).
"""

from collections import deque
from dataclasses import dataclass, field

from pewpy.tools.boss_candidates.canvas import Canvas

Cells = dict[tuple[int, int, int], str]  # (column, row, layer) -> character; layers negative up (the game's)


@dataclass(frozen=True)
class Shaping:
    """What each character of a plan is in 3D (its role), and how big things get."""

    roles: dict[str, str]  # character -> "hull", "seam", "wing", "pod", "gun" or "raised"
    tiers: dict[str, int] = field(default_factory=dict)  # a raised character's tier
    top: int = 2  # the hull's highest point above the middle plane...
    bottom: int = 1  # ...and its lowest below it
    edge: int = 0  # the hull's top at its outline...
    slope: int = 2  # ...rising this much a cube inwards, up to `top` (the chamfer)
    tier_height: int = 1  # how much each tier adds, at most
    pod: int = 1  # a pod's half height, at most
    wing: int = 1  # a wing's thickness
    gun: int = 0  # the height of the guns' barrels
    lift: float = 0.06  # a wing rises this many cubes per cube away from the hull
    fill: str = "h"  # under a raised cell
    underside: str = "D"  # the lowest cube of the hull's plating
    plating: str = "hHN"  # which hull characters get the darker underside


def distances(region: set[tuple[int, int]]) -> dict[tuple[int, int], int]:
    """How far each cell of `region` is from its outline: 1 next to a cell outside it, then 2..."""
    result: dict[tuple[int, int], int] = {}
    queue: deque[tuple[int, int]] = deque()
    for x, y in region:
        if any((x + dx, y + dy) not in region for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            result[x, y] = 1
            queue.append((x, y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in region and cell not in result:
                result[cell] = result[x, y] + 1
                queue.append(cell)
    return result


def _reach(region: set[tuple[int, int]], sources: set[tuple[int, int]]) -> dict[tuple[int, int], int]:
    """How far each cell of `region` is from the nearest of `sources` (next to them: 1), through the region."""
    result: dict[tuple[int, int], int] = {}
    queue: deque[tuple[int, int]] = deque()
    for x, y in region:
        if any((x + dx, y + dy) in sources for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            result[x, y] = 1
            queue.append((x, y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in region and cell not in result:
                result[cell] = result[x, y] + 1
                queue.append(cell)
    return result


def sculpt(cv: Canvas, shaping: Shaping) -> tuple[Cells, dict[tuple[int, int], tuple[int, int]]]:
    """Return the model's cubes, and each column's (bottom, top) heights (z up) for placing things on it."""
    role = {(x, y): shaping.roles.get(cv.get(x, y), "hull") for x, y in cv.cells_of(cv.rows_chars())}
    body = {cell for cell, kind in role.items() if kind in ("hull", "seam", "raised")}
    heights = _body_heights(cv, shaping, role, body)
    cells = _body_cells(cv, shaping, role, heights)
    _add_wings(cv, shaping, role, body, cells, heights)
    pods = {cell for cell, kind in role.items() if kind == "pod"}
    for (x, y), d in distances(pods).items():
        half = min(shaping.pod, d)
        for z in range(-half, half + 1):
            cells[x, y, -z] = cv.get(x, y)
        heights[x, y] = (-half, half)
    for (x, y), kind in role.items():
        if kind == "gun":
            cells[x, y, -shaping.gun] = cv.get(x, y)
            heights[x, y] = (shaping.gun, shaping.gun)
    return cells, heights


def _body_heights(
    cv: Canvas, shaping: Shaping, role: dict[tuple[int, int], str], body: set[tuple[int, int]]
) -> dict[tuple[int, int], tuple[int, int]]:
    """Each body column's (bottom, top): the chamfered hull, with the raised tiers stacked on it."""
    heights: dict[tuple[int, int], tuple[int, int]] = {}
    for cell, d in distances(body).items():
        heights[cell] = (-min(shaping.bottom, (d + 1) // 2), min(shaping.top, shaping.edge + shaping.slope * (d - 1)))
    for tier in range(1, max(shaping.tiers.values(), default=0) + 1):
        region = {cell for cell in body if role[cell] == "raised" and shaping.tiers.get(cv.get(*cell), 1) >= tier}
        for cell, d in distances(region).items():
            bottom, top = heights[cell]
            heights[cell] = (bottom, top + min(shaping.tier_height, d))
    return heights


def _body_cells(
    cv: Canvas, shaping: Shaping, role: dict[tuple[int, int], str], heights: dict[tuple[int, int], tuple[int, int]]
) -> Cells:
    """Return the body's cubes (seams lose their top cube, in `heights` too)."""
    cells: Cells = {}
    for (x, y), (bottom, full_top) in heights.items():
        char = cv.get(x, y)
        top = full_top
        if role[x, y] == "seam":
            top = max(bottom, full_top - 1)
            heights[x, y] = (bottom, top)
        for z in range(bottom, top + 1):
            if role[x, y] == "raised" and z < top:
                cells[x, y, -z] = shaping.fill
            elif z == bottom and z < 0 and char in shaping.plating:
                cells[x, y, -z] = shaping.underside
            else:
                cells[x, y, -z] = char
    return cells


def _add_wings(
    cv: Canvas,
    shaping: Shaping,
    role: dict[tuple[int, int], str],
    body: set[tuple[int, int]],
    cells: Cells,
    heights: dict[tuple[int, int], tuple[int, int]],
) -> None:
    """Add the wings' cubes and heights: thin plates rising towards their tips, thicker at their roots."""
    wings = {cell for cell, kind in role.items() if kind == "wing"}
    root = _reach(wings, body)
    for x, y in wings:
        out = root.get((x, y))
        z = round(out * shaping.lift) if out is not None else 0
        thickness = shaping.wing + (1 if out is not None and out <= 2 else 0)
        for layer in range(z - thickness + 1, z + 1):
            cells[x, y, -layer] = cv.get(x, y)
        heights[x, y] = (z - thickness + 1, z)


def lifted(cells: Cells, by: int) -> Cells:
    """Return the same cubes `by` cubes higher (towards the camera)."""
    return {(x, y, layer - by): char for (x, y, layer), char in cells.items()}


def engines_at_height(engines: list[dict], heights: dict[tuple[int, int], tuple[int, int]]) -> list[dict]:
    """Each engine's flame at the middle of its nozzle's column (engines without a column there stay at 0)."""
    result = []
    for engine in engines:
        bottom, top = heights.get((round(engine["x"]), round(engine["y"])), (0, 0))
        z = (bottom + top) / 2
        result.append({**engine, "z": z} if z else dict(engine))
    return result
