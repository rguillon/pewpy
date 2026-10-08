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
POWER = "power"
VENT = "vent"

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
    part.weapon("gun", 0, size - 1, 0)
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


def _twin_cannon(_rng: object, size: int) -> Part:
    """Return a twin cannon: two parallel barrels `size` cubes long."""
    part = Part()
    spread = max(1, size // 2)
    for step in range(size):
        for side in (-spread, spread):
            part.put(side, step, 0, "r" if step == size - 1 else "h")
    part.weapon("gun", -spread, size - 1, 0)
    part.weapon("gun", spread, size - 1, 0)
    return part


def _gatling(_rng: object, size: int) -> Part:
    """Return a gatling gun: a cluster of barrels `size` cubes long."""
    part = Part()
    barrels = max(2, size)
    for step in range(size):
        for b in range(barrels):
            bx = round(0.8 * size * (b - barrels // 2 + 0.5) / max(1, barrels - 1))
            part.put(bx, step, 0, "r" if step == size - 1 else "h")
    for b in range(barrels):
        bx = round(0.8 * size * (b - barrels // 2 + 0.5) / max(1, barrels - 1))
        part.weapon("gatling", bx, size - 1, 0)
    return part


def _flak_gun(_rng: object, size: int) -> Part:
    """Return a flak gun: a short, wide barrel with a muzzle brake."""
    part = Part()
    r = max(1, size // 2)
    for step in range(size):
        rad = r if step < size - 1 else r + 1
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, step, dz, "r" if step == size - 1 else "N")
    part.weapon("flak", 0, size - 1, 0)
    return part


def _beam_emitter(_rng: object, size: int) -> Part:
    """Return a beam emitter: a glowing crystal in a housing."""
    part = Part()
    part.housing(size // 2 + 1, 0, size, 0, size // 2 + 1)
    for step in range(size):
        part.put(0, step, 0, "G")
    part.weapon("laser", 0, size - 1, 0)
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


def _big_engine(_rng: object, size: int) -> Part:
    """Return a big engine for bosses: a large nozzle with vents."""
    part = Part()
    r = max(1, size)
    for z in range(r + 1):
        rad = r - z + 1
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, 0, z, "N" if z == 0 else "h")
    part.nozzle(0, 0, 0, float(r))
    return part


def _exhaust_stacks(_rng: object, size: int) -> Part:
    """Return exhaust stacks: multiple small nozzles."""
    part = Part()
    count = max(2, size)
    spread = max(1, size // 2)
    for i in range(count):
        x = (i - (count - 1) / 2) * spread
        part.put(int(x), 0, 0, "o")
        part.nozzle(int(x), 0, 0, 0.5)
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


def _big_wing(_rng: object, size: int) -> Part:
    """Return a big wing for bosses: a wide, swept plate."""
    part = Part()
    chord = max(4, size * 3)
    span = max(3, size * 2)
    for y in range(chord):
        w = span - y // 2
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


def _flying_wing(_rng: object, size: int) -> Part:
    """Return a flying wing: a wide, thin delta shape."""
    part = Part()
    chord = max(3, size * 2)
    for y in range(chord):
        w = (chord - y) * 2
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


def _reactor(_rng: object, size: int) -> Part:
    """Return a reactor: a glowing core in a housing."""
    part = Part()
    r = max(1, size)
    part.housing(r, 0, r * 2, 0, r)
    for z in range(r + 1):
        rad = r - z
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, r, z, "G")
    return part


def _radar(_rng: object, size: int) -> Part:
    """Return a radar dish: a parabolic reflector on a mast."""
    part = Part()
    r = max(1, size)
    for z in range(r + 1):
        rad = r - z
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, 0, z, "S")
    part.put(0, 0, r + 1, "h")
    return part


def _antenna(_rng: object, size: int) -> Part:
    """Return an antenna: a thin spike with a tip light."""
    part = Part()
    for z in range(size + 1):
        part.put(0, 0, z, "h")
    part.put(0, 0, size + 1, "p")
    return part


def _sensor_dome(_rng: object, size: int) -> Part:
    """Return a sensor dome: a hemispherical blister."""
    part = Part()
    r = max(1, size)
    part.dome(0, float(r), 0, "S")
    return part


def _vent(_rng: object, size: int) -> Part:
    """Return a vent: a recessed grille."""
    part = Part()
    r = max(1, size)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                part.put(dx, 0, dz, "k")
    return part


def _radiator(_rng: object, size: int) -> Part:
    """Return a radiator: a flat panel with fins."""
    part = Part()
    r = max(1, size)
    for x in range(-r, r + 1):
        for y in range(r + 1):
            part.put(x, y, 0, "H" if y % 2 == 0 else "h")
    return part


def _fuel_tank(_rng: object, size: int) -> Part:
    """Return a fuel tank: a cylindrical tank with caps."""
    part = Part()
    r = max(1, size)
    for y in range(r * 2 + 1):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    part.put(dx, y, dz, "t")
    return part


# Register all parts
register("cube", _cube, tags=[HULL])
register("nose_gun", _nose_gun, tags=[WEAPON, GUN])
register("turret", _turret, tags=[WEAPON, GUN])
register("twin_cannon", _twin_cannon, tags=[WEAPON, GUN])
register("gatling", _gatling, tags=[WEAPON, GUN])
register("flak_gun", _flak_gun, tags=[WEAPON, GUN])
register("beam_emitter", _beam_emitter, tags=[WEAPON, GUN])
register("missile_rack", _missile_rack, tags=[WEAPON, MISSILE])
register("tail_engine", _tail_engine, tags=[ENGINE])
register("big_engine", _big_engine, tags=[ENGINE])
register("exhaust_stacks", _exhaust_stacks, tags=[ENGINE])
register("wing_root", _wing_root, tags=[WING, STORES])
register("big_wing", _big_wing, tags=[WING, STORES])
register("flying_wing", _flying_wing, tags=[WING, STORES])
register("reactor", _reactor, tags=[POWER])
register("radar", _radar, tags=[SENSOR])
register("antenna", _antenna, tags=[SENSOR])
register("sensor_dome", _sensor_dome, tags=[SENSOR])
register("vent", _vent, tags=[VENT])
register("radiator", _radiator, tags=[VENT])
register("fuel_tank", _fuel_tank, tags=[STORES])


# ---- Convenience ----


def get_part(name: str, rng: object, size: int) -> Part:
    """Build a part by name `size` big, using `rng` for randomness."""
    if name not in PARTS:
        msg = f"unknown part: {name}"
        raise ValueError(msg)
    return PARTS[name](rng, size)


PART_NAMES = sorted(PARTS.keys())
