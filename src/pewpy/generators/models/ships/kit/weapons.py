"""The weapons: nose barrels, wing and tip guns, missiles, a turret, a gatling, a side cannon.

Barrels point forward (towards the nose, the last row): missiles under the wings, the turret on top, the gatling
under the nose, the big cannon on one side only.
"""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.components import Piece
from pewpy.generators.models.components.gatling import gatling as gatling_piece
from pewpy.generators.models.components.turret import turret as turret_piece
from pewpy.generators.models.ships.kit.hulls import Hull
from pewpy.generators.models.ships.kit.ship import Ship
from pewpy.generators.models.ships.kit.wings import Wing

# A gatling's barrels, seen from the front: (x, z) offsets.


def nose_guns(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put one barrel on the nose, or two on its sides."""
    y = hull.length - 1
    z = (hull.top_at(y) + hull.bottom_at(y)) // 2
    reach = rng.randint(2, 3)
    if rng.random() < 0.5:
        ship.box(0, 0, y + 1, y + reach, z, z, "r")
        ship.weapon("gun", 0, y + reach, z)
        return
    back = max(0, hull.length - 3)
    x = -max(1, round(hull.half(back)))
    ship.box(x, x, back, y + reach - 1, z, z, "r")
    ship.weapon("gun", x, y + reach - 1, z)


def wing_guns(rng: Rng, ship: Ship, wing: Wing, share: float) -> None:
    """Put a gun on each wing's leading edge, `share` of the way out, its barrel pointing forward."""
    xs = sorted(wing.leading)
    if not xs:
        return
    x = xs[min(len(xs) - 1, round((1 - share) * (len(xs) - 1)))]
    y, z = wing.leading[x]
    tip = y + rng.randint(2, 4)
    ship.box(x, x, y - 1, tip, z - 1, z - 1, "r")
    ship.box(x, x, y - 2, y, z - 1, z - 1, "N")
    ship.weapon("gun", x, tip, z - 1)


def tip_weapons(rng: Rng, ship: Ship, wing: Wing) -> None:
    """Put a gun or a missile on each wing's tip."""
    if not wing.tip:
        return
    x, y, z = wing.tip[len(wing.tip) // 2]
    front = max(cy for _, cy, _ in wing.tip)
    if rng.random() < 0.5:
        ship.box(x, x, y - 1, front + 2, z, z, "r")
        ship.weapon("gun", x, front + 2, z)
    else:
        ship.box(x, x, y - 2, front + 1, z - 1, z - 1, "H")
        ship.put(x, front + 2, z - 1, "p")
        ship.weapon("missile", x, front + 2, z - 1)


def missiles(rng: Rng, ship: Ship, wing: Wing) -> None:
    """Hang missiles under the wing, light bodies with marked tips."""
    xs = sorted(wing.leading)
    for x in xs[1 : len(xs) - 1 : max(2, len(xs) // rng.randint(2, 3))]:
        y, z = wing.leading[x]
        ship.box(x, x, y - 3, y, z - 2, z - 2, "H")
        ship.put(x, y + 1, z - 2, "p")
        ship.weapon("missile", x, y + 1, z - 2)


def turret(rng: Rng, ship: Ship, hull: Hull, y: int) -> None:
    """Put a built-in turret on the spine, its middle at row y, its barrels pointing forward."""
    piece = turret_piece(rng, 1)
    ship.stamp(piece, 0, y - middle(piece), hull.top_at(y) + 1)


def gatling(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a built-in gatling under the nose, hanging from the hull, its barrels reaching past the nose."""
    piece = gatling_piece(rng, 1)
    y = hull.length - 2
    ship.stamp(piece, 0, y - middle(piece), hull.bottom_at(y) - piece.height())


def middle(piece: Piece) -> int:
    """Return a built-in part's middle row (its rows from its back)."""
    return max(y for _, y in piece.footprint()) // 2


def side_cannon(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a big cannon on one side only: a housing along the hull and a long barrel (the ship is lopsided)."""
    y = hull.widest(0.3, 0.7)
    x = -round(hull.half(y)) - 2
    z = (hull.top_at(y) + hull.bottom_at(y)) // 2
    back = max(0, y - rng.randint(3, 5))
    for cy in range(back, y + 2):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                ship.put(x + dx, cy, z + dz, "N" if (cy + dx) % 3 else "k", mirror=False)
    front = max(hull.length, y + 6)
    for cy in range(y + 2, front):
        ship.put(x, cy, z, "r", mirror=False)
    ship.put(x, front, z, "R", mirror=False)
    ship.weapon("cannon", x, front, z, mirror=False)
