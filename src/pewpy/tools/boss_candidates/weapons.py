"""A boss's weapons: its parts' barrels, and guns on the front of its core.

A part's weapons are its barrels ("r"): each group of barrel cubes touching each other is one weapon, firing from the
middle of its front row; a missile launcher or pod, or an emitter, fires from the middle of its front edge. Their kind
comes from the part's (PART_WEAPONS). The core gets guns on its front edge, barrels sticking out towards the nose,
enough for the boss to have at least MIN_WEAPONS with its parts (and at least a pair).
"""

from pewpy.tools.boss_candidates.canvas import Canvas

MIN_WEAPONS = 5  # on a boss, its parts' and its core's
CORE_GUNS = 2  # at least, on the core
BARREL = 3  # cubes a core gun sticks out
GUN_SPACING = 4  # cubes at least between two core guns
PART_WEAPONS = {  # a part's kind: its weapons' kind
    "turret": "turret",
    "cannon": "cannon",
    "flak": "flak",
    "launcher": "missile",
    "missile_pod": "missile",
    "emitter": "laser",
}
FRONT_FIRING = ("launcher", "missile_pod", "emitter")  # batteries and emitters: they fire from their front edge

Weapon = tuple[str, float, float]  # (kind, column, row of its barrel's tip)


def part_weapons(cv: Canvas, kind: str) -> list[Weapon]:
    """Return a part's weapons."""
    if kind not in PART_WEAPONS:
        return []
    weapon = PART_WEAPONS[kind]
    if kind in FRONT_FIRING:
        middle = cv.w // 2
        front = max(y for y in range(cv.h) if cv.filled(middle, y))
        return [(weapon, middle, front)]
    found = []
    for group in _groups(set(cv.cells_of("r"))):
        front = max(y for _, y in group)
        xs = sorted(x for x, y in group if y == front)
        found.append((weapon, xs[len(xs) // 2], front))
    return found


def core_guns(cv: Canvas, wanted: int, symmetric: bool) -> list[Weapon]:
    """Put `wanted` guns (or a few more, to keep a symmetric boss symmetric) on the core's front edge.

    The most forward columns first, spread out; the canvas grows at the front (its last rows) for the barrels, so
    nothing measured from its back moves. Return the guns.
    """
    middle = (cv.w - 1) / 2
    fronts = {x: max((y for y in range(cv.h) if cv.filled(x, y)), default=-1) for x in range(cv.w)}
    columns = [x for x, front in fronts.items() if front >= 0 and cv.get(x, front) not in "xo"]
    if symmetric:
        columns = [x for x in columns if x <= middle]
    for spacing in range(GUN_SPACING, 1, -1):  # closer together if they don't fit
        chosen = _spread(
            sorted(columns, key=lambda x: (-fronts[x], abs(x - middle))), spacing, wanted, symmetric, middle
        )
        if sum(2 if symmetric and x != middle else 1 for x in chosen) >= wanted:
            break
    if symmetric:
        chosen += [round(2 * middle - x) for x in chosen if x != middle]
    guns = []
    for x in chosen:
        tip = fronts[x] + BARREL
        while cv.h <= tip:
            cv.cells.append(["."] * cv.w)
            cv.h += 1
        for y in range(fronts[x] + 1, tip + 1):
            cv.set(x, y, "r")
        guns.append(("gun", x, tip))
    return guns


def _spread(columns: list[int], spacing: int, wanted: int, symmetric: bool, middle: float) -> list[int]:
    """Pick columns in order, `spacing` apart at least, until there are `wanted` guns (counting mirror images)."""
    chosen: list[int] = []
    for x in columns:
        if all(abs(x - other) >= spacing for other in chosen):
            chosen.append(x)
        if sum(2 if symmetric and x != middle else 1 for x in chosen) >= wanted:
            break
    return chosen


def _groups(cells: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Split cells into groups touching each other (sides only)."""
    groups, seen = [], set()
    for start in sorted(cells):
        if start in seen:
            continue
        group, todo = [], [start]
        seen.add(start)
        while todo:
            x, y = todo.pop()
            group.append((x, y))
            for near in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if near in cells and near not in seen:
                    seen.add(near)
                    todo.append(near)
        groups.append(group)
    return groups
