"""The extras: fins, antennas, a radar dome, intakes, armor, equipment; the paint (a livery, a nose cone, stripes)."""

from pewpy.makers.common.geometry import Rng
from pewpy.makers.components import COMPONENTS
from pewpy.makers.ships.kit.hulls import Hull
from pewpy.makers.ships.kit.ship import Ship


def fins(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put upright fins at the tail, taller towards the back: one on the spine, or two on the sides."""
    length = max(2, round(hull.length * rng.uniform(0.15, 0.25)))
    tall = rng.randint(2, 4)
    twin = rng.random() < 0.5 and hull.half(1) >= 1.5
    x = -round(hull.half(1)) + 1 if twin else 0
    for y in range(length):
        base = hull.top_at(y) + 1
        height = max(1, round(tall * (1 - y / length) + 0.5))
        for dz in range(height):
            ship.put(x, y, base + dz, "S" if y else "k")
    ship.put(x, 0, hull.top_at(0) + tall, "R" if rng.random() < 0.4 else "S")


def antenna(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a thin mast with a glowing tip, or two whips on the sides."""
    y = round(hull.length * rng.uniform(0.25, 0.5))
    if rng.random() < 0.5:
        z = hull.top_at(y) + 1
        tall = rng.randint(2, 3)
        ship.box(0, 0, y, y, z, z + tall - 1, "k")
        ship.put(0, y, z + tall, "R")
    else:
        x = -round(hull.half(y))
        z = hull.top_at(y) // 2
        ship.box(x, x, max(0, y - 4), y, z + 1, z + 1, "k")
        ship.put(x, max(0, y - 4), z + 2, "R")


def dome(_rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a small radar dome on the spine, behind the middle."""
    y = round(hull.length * 0.35)
    z = hull.top_at(y) + 1
    ship.box(-1, 0, y - 1, y + 1, z, z, "t")
    ship.put(0, y, z + 1, "t")


def intakes(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put dark air intakes on the hull's sides, in front of the middle."""
    y = round(hull.length * rng.uniform(0.55, 0.7))
    x = -round(hull.half(y)) - 1
    for cy in range(y - 2, y + 1):
        ship.put(x, cy, 0, "N")
        ship.put(x, cy, 1, "N" if cy < y else "k")


def armor(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put heavy plates along the hull's sides."""
    first = round(hull.length * rng.uniform(0.2, 0.35))
    last = round(hull.length * rng.uniform(0.55, 0.75))
    for y in range(first, last + 1):
        x = -round(hull.half(y)) - 1
        for z in range(hull.bottom_at(y) // 2, hull.top_at(y) // 2 + 1):
            ship.put(x, y, z, "k" if y in (first, last) else "N")


def livery(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Paint a stripe of the livery across the hull's top (and the wings under it)."""
    y = round(hull.length * rng.uniform(0.3, 0.6))
    wide = rng.randint(1, 2)
    tops = ship.tops()
    for (x, cy, z), char in list(ship.cells.items()):
        if y <= cy < y + wide and char in "hHwWk" and z == tops[x, cy]:
            ship.cells[x, cy, z] = "L"


def markings(rng: Rng, ship: Ship) -> None:
    """Paint markings on the wings: a chevron near each tip."""
    wing = [(x, y, z) for (x, y, z), char in ship.cells.items() if char in "wW" and x < -2]
    if not wing:
        return
    far = min(x for x, _, _ in wing)
    tops = ship.tops()
    for x, y, z in wing:
        if x <= far + rng.randint(1, 2) and tops[x, y] == z:
            ship.put(x, y, z, "q")


def nose_cone(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Paint the nose's last few rows in the accent color."""
    first = hull.length - rng.randint(2, 4)
    for (x, y, z), char in list(ship.cells.items()):
        if y >= first and char in "hHSDk" and abs(x) <= round(hull.half(y)) + 1:
            ship.cells[x, y, z] = "p"


def wing_stripes(rng: Rng, ship: Ship) -> None:
    """Paint a stripe of the livery along each wing, from root to tip, a few rows behind its leading edge."""
    wings = [(x, y, z) for (x, y, z), char in ship.cells.items() if char in "wW"]
    if not wings:
        return
    rows = sorted({y for _, y, _ in wings})
    stripe = rows[len(rows) // 2 :][: rng.randint(1, 2)]
    for x, y, z in wings:
        if y in stripe:
            ship.cells[x, y, z] = "L"


EQUIPMENT = ("vent", "radiator", "antenna", "stack", "tank", "missile_rack", "dome")  # built-in parts a hull carries


def equipment(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put one or two small built-in parts (see EQUIPMENT) on the hull's top: on the spine, or a pair on its sides."""
    for _ in range(rng.randint(1, 2)):
        piece = COMPONENTS[rng.choice(EQUIPMENT)](rng, 1)
        y = rng.randint(hull.length // 4, max(hull.length // 4, hull.length * 2 // 3 - 3))
        x = 0 if rng.random() < 0.5 else -max(2, round(hull.half(y)) - 1)
        ship.stamp(piece, x, y, hull.top_at(y) + 1)
