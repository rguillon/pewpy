"""The cockpits, on top of the hull towards its nose.

A bubble canopy, a long canopy, a visor across the nose, an armored bridge, or just a sensor eye (for drones).
"""

from collections.abc import Callable

from pewpy.generators.models.common.geometry import Rng
from pewpy.generators.models.ships.kit.hulls import Hull
from pewpy.generators.models.ships.kit.ship import Ship


def bubble(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a bubble canopy, rounded, a frame behind it."""
    y = round(hull.length * rng.uniform(0.6, 0.75))
    long = max(1, round(hull.length * 0.1))
    wide = 1 if hull.half(y) >= 1.8 else 0
    z = hull.top_at(y) + 1
    for dy in range(-long, long + 1):
        reach = wide if abs(dy) < long else 0
        ship.box(-reach, 0, y + dy, y + dy, z, z, "c")
    if long >= 2:
        ship.box(0, 0, y - long + 1, y + long - 1, z + 1, z + 1, "c")
    ship.box(-wide, 0, y - long - 1, y - long - 1, z, z, "S")  # the frame


def canopy(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a long narrow canopy along the spine, a sensor at its front."""
    front = round(hull.length * rng.uniform(0.7, 0.8))
    long = max(2, round(hull.length * 0.22))
    for y in range(front - long, front + 1):
        ship.put(0, y, hull.top_at(y) + 1, "c")
    ship.put(0, front + 1, hull.top_at(front + 1) + 1, "S")


def visor(_rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a band of windows across the nose's top."""
    for y in range(max(0, hull.length - 3), hull.length - 1):
        reach = round(hull.half(y) * 0.6)
        ship.box(-reach, 0, y, y, hull.top_at(y), hull.top_at(y), "c")


def bridge(rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put an armored bridge: a raised block, windows along its front, a mast on it."""
    y = round(hull.length * rng.uniform(0.45, 0.65))
    wide = max(1, round(hull.half(y) * 0.45))
    z = hull.top_at(y) + 1
    ship.box(-wide, 0, y - 2, y + 1, z, z + 1, "S")
    ship.box(-wide, 0, y + 1, y + 1, z + 1, z + 1, "c")
    ship.box(0, 0, y - 1, y - 1, z + 2, z + 3, "k")
    ship.put(0, y - 1, z + 4, "R")


def eye(_rng: Rng, ship: Ship, hull: Hull) -> None:
    """Put a glowing sensor eye on the nose."""
    y = hull.length - 1
    z = (hull.top_at(y) + hull.bottom_at(y)) // 2
    ship.box(0, 0, y, y + 1, z, z, "R")


COCKPITS: dict[str, Callable[[Rng, Ship, Hull], None]] = {
    "bubble": bubble,
    "canopy": canopy,
    "visor": visor,
    "bridge": bridge,
    "eye": eye,
}
