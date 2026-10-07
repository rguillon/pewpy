"""The engines: nozzles at the tail, or nacelles (pods) on the wings or the hull's sides."""

from pewpy.generators.models.ships.kit.hulls import Hull
from pewpy.generators.models.ships.kit.ship import Ship

# Nozzle cross-sections, hardcoded: (x, z) offsets from the nozzle's middle, by size. "o" is the nozzle's mouth,
# "N" the housing round it.
NOZZLES: dict[int, dict[tuple[int, int], str]] = {
    1: {(0, 0): "o"},
    2: {(0, 0): "o", (-1, 0): "N", (1, 0): "N", (0, 1): "N", (0, -1): "D"},
    3: {
        **{(x, z): "o" for x in (-1, 0, 1) for z in (-1, 0, 1) if abs(x) + abs(z) < 2},
        **{(x, z): "N" for x in (-2, 2) for z in (-1, 0, 1)},
        **{(x, z): "N" for x in (-1, 0, 1) for z in (2,)},
        **{(x, z): "D" for x in (-1, 0, 1) for z in (-2,)},
    },
}


def tail_engines(ship: Ship, hull: Hull, count: int, size: int, depth: int = 2) -> None:
    """Put `count` engines at the hull's tail, side by side, `depth` cubes of housing sticking out behind it.

    Nozzles are `size` 1 to 3 (bigger asks get the biggest).
    """
    size = min(size, max(NOZZLES))
    z = (hull.top_at(0) + hull.bottom_at(0)) // 2
    half = hull.half(0)
    spacing = max(size + 1, round(half * 2 / max(1, count)))
    offsets = [0] if count == 1 else [-spacing // 2 - spacing * i for i in range(count // 2)]
    if count == 3:
        offsets = [0, -spacing]
    for x in offsets:
        for y in range(-depth, 1):
            for (dx, dz), char in NOZZLES[size].items():
                paint = char if y == -depth else ("N" if char == "o" else char)
                ship.put(x + dx, y, z + dz, paint)
        ship.nozzle(x, -depth, z, size + 0.6)


def nacelle(ship: Ship, x: int, z: int, back: int, length: int, size: int = 2) -> None:
    """Put an engine pod (and its mirror image) running `length` cubes forward from `back`: an intake at its front.

    Its length is made to the ship's fit.
    """
    length = ship.fitted(length, 2)
    shape = NOZZLES[min(size, 3)]
    for y in range(back, back + length):
        for (dx, dz), char in shape.items():
            if y == back:
                paint = char
            elif y >= back + length - 1:
                paint = "k" if char == "o" else "H"  # the intake
            else:
                paint = "h" if (y - back) % 3 else "H"
                if char == "D":
                    paint = "D"
            ship.put(x + dx, y, z + dz, paint)
    ship.nozzle(x, back, z, size + 0.4)
