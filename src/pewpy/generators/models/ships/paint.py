"""A ship's paint, once its parts are placed: a livery stripe, a nose cone, wing stripes, markings on the wing tips.

Its main color stays its greys: only bits are painted.
"""

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.ships.ship import Ship


def livery(rng: Rng, ship: Ship, length: int) -> None:
    """Paint a stripe of the livery across the top of the ship (hull and wings), `length` the hull's."""
    y = round(length * rng.uniform(0.3, 0.6))
    wide = rng.randint(1, 2)
    for (x, cy, z), char in list(ship.cells.items()):
        if y <= cy < y + wide and char in "hHwWk" and z == ship.tops[x, cy]:
            ship.cells[x, cy, z] = "L"


def nose_cone(rng: Rng, ship: Ship, length: int, half: int) -> None:
    """Paint the hull's last few rows in the accent color (`half`: how far it is from the axis to its side)."""
    first = length - rng.randint(2, 4)
    for (x, y, z), char in list(ship.cells.items()):
        if first <= y < length and char in "hHSDk" and abs(x) <= half:
            ship.cells[x, y, z] = "p"


def wing_stripes(rng: Rng, ship: Ship) -> None:
    """Paint a stripe of the livery along the wings, from root to tip, a few rows behind their leading edge."""
    wings = [(x, y, z) for (x, y, z), char in ship.cells.items() if char in "wW"]
    if not wings:
        return
    rows = sorted({y for _, y, _ in wings})
    stripe = rows[len(rows) // 2 :][: rng.randint(1, 2)]
    for x, y, z in wings:
        if y in stripe:
            ship.cells[x, y, z] = "L"


def markings(rng: Rng, ship: Ship) -> None:
    """Paint markings near the tip of each wing (the wing cubes farthest out on each side)."""
    reach = rng.randint(1, 2)
    for side in (-1, 1):
        wing = [(x, y, z) for (x, y, z), char in ship.cells.items() if char in "wW" and x * side > 2]
        if not wing:
            continue
        far = max(x * side for x, _, _ in wing)
        for x, y, z in wing:
            if x * side >= far - reach and ship.tops[x, y] == z:
                ship.cells[x, y, z] = "q"
