"""The library of prebuilt parts: every part the assembler can use.

Each entry maps a part name to a function `(rng, size) -> Part`. Parts are parametric: `size` 1 is
ship-sized, more on a boss. Every part uses the palette characters so the same part goes on a ship and on a boss.

See `pewpy.generators.models.library` for the `Part` dataclass and its transforms.
"""

from collections import defaultdict
from collections.abc import Callable

from pewpy.generators.models.library.part import Part

# ---- Part kind tags ----
HULL = "hull"
WING = "wing"
ENGINE = "engine"
WEAPON = "weapon"
GUN = "gun"
MISSILE = "missile"
COCKPIT = "cockpit"
SENSOR = "sensor"
PLATING = "plating"
STORES = "stores"

# ---- The catalog ----

#: All parts, by name. Each is (rng, size) -> Part.
PARTS: dict[str, Callable] = {}

#: Parts grouped by tag, for matching to slots.
BY_TAG: dict[str, list[str]] = defaultdict(list)


def register(name: str, build: Callable[[object, int], Part], *, tags: list[str] | None = None) -> None:
    """Register a part: `build` is `(rng, size) -> Part`."""
    PARTS[name] = build
    if tags:
        for tag in tags:
            BY_TAG[tag].append(name)


# ---- Simple part builders that accept (rng, size) ----


def _cube(_rng: object, size: int) -> Part:
    """Return a `size` cube of cubes."""
    part = Part()
    for y in range(size):
        for z in range(size):
            for x in range(size):
                part.put(x - size // 2, y, z, "h")
    return part


def _nose_gun(_rng: object, size: int) -> Part:
    """Return a nose gun `size` cubes long."""
    part = Part()
    for step in range(size):
        part.put(0, step, 0, "r" if step < size - 1 else "p")
    return part


def _turret(_rng: object, size: int) -> Part:
    """Return a turret `size` big."""
    part = Part()
    r = size
    for z in range(r + 1):
        rad = r - z + 1
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, 0, z, "N" if z == 0 else "h")
    tip_z = r + 1
    part.put(0, tip_z, 0, "r")
    part.weapon("turret", 0, tip_z, 0)
    return part


def _missile_rack(_rng: object, size: int) -> Part:
    """Return a missile rack `size` big."""
    part = Part()
    front = size + 1
    part.housing(size // 2 + 1, 0, front, 0, size // 2 + 1)
    part.box(0, 0, front + 1, front + 1, 0, 0, "p")
    part.weapon("missile", 0, front + 1, 0)
    return part


def _tail_engine(_rng: object, _size: int) -> Part:
    """Return a tail engine `size` big."""
    part = Part()
    part.put(0, 0, 0, "o")
    return part


def _wing_root(_rng: object, size: int) -> Part:
    """Return a wing root: a plate chord cubes long at the wing root."""
    part = Part()
    chord = max(2, size + 2)  # make it bigger for bigger ships
    for y in range(chord):
        w = chord - y
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


# Register all parts
register("cube", _cube, tags=[HULL])
register("nose_gun", _nose_gun, tags=[WEAPON, GUN])
register("turret", _turret, tags=[WEAPON, GUN])
register("missile_rack", _missile_rack, tags=[WEAPON, MISSILE])
register("tail_engine", _tail_engine, tags=[ENGINE])
register("wing_root", _wing_root, tags=[WING, STORES])


# ---- Convenience ----


def get_part(name: str, rng: object, size: int) -> Part:
    """Build a part by name `size` big, using `rng` for randomness."""
    if name not in PARTS:
        msg = f"unknown part: {name}"
        raise ValueError(msg)
    return PARTS[name](rng, size)


PART_NAMES = sorted(PARTS.keys())
