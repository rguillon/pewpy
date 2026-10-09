"""Guns on the front of a boss's core.

A boss's parts' weapons are their catalog parts' (see modules.py). The core gets guns on its front edge, barrels
sticking out towards the nose, enough for the boss to have at least MIN_WEAPONS with its parts (and at least a pair);
the guns stamped on its hull (see greebles.py) come on top.
"""

from pewpy.generators.models.bosses.canvas import Canvas

MIN_WEAPONS = 5  # on a boss, its parts' and its core's
CORE_GUNS = 2  # at least, on the core
BARREL = 3  # cubes a core gun sticks out
GUN_SPACING = 4  # cubes at least between two core guns
Weapon = tuple[str, float, float]  # (kind, column, row of its barrel's tip)


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
