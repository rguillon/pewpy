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


def _heavy_cannon(_rng: object, size: int) -> Part:
    """Return a heavy cannon: a thick barrel with muzzle brake and housing."""
    part = Part()
    r = max(1, size // 2)
    part.housing(r + 1, 0, size, 0, r)
    for step in range(size):
        rad = r if step < size - 1 else r + 1
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, step, dz, "r" if step >= size - 2 else "N")
    part.weapon("cannon", 0, size - 1, 0)
    return part


def _plasma_gun(_rng: object, size: int) -> Part:
    """Return a plasma gun: a glowing core with coils around it."""
    part = Part()
    r = max(1, size // 2)
    part.housing(r + 1, 0, size, 0, r)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    part.put(dx, step, dz, "G" if step % 2 == 0 else "R")
    part.weapon("plasma", 0, size - 1, 0)
    return part


def _railgun(_rng: object, size: int) -> Part:
    """Return a railgun: long parallel rails with a glowing tip."""
    part = Part()
    spread = max(1, size // 3)
    for step in range(size):
        for side in (-spread, spread):
            part.put(side, step, 0, "H" if step % 3 == 0 else "N")
    part.put(0, size - 1, 0, "G")
    part.weapon("railgun", 0, size - 1, 0)
    return part


def _missile_pod(_rng: object, size: int) -> Part:
    """Return a missile pod: a box with multiple missile tubes."""
    part = Part()
    r = max(1, size // 2)
    part.housing(r + 1, 0, size, 0, r)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    part.put(dx, step, dz, "t" if step == size - 1 else "N")
    for dx in range(-r + 1, r):
        for dz in range(-r + 1, r):
            if dx * dx + dz * dz <= (r - 1) * (r - 1):
                part.put(dx, size, dz, "p")
                part.weapon("missile", dx, size, dz)
    return part


def _flak_turret(_rng: object, size: int) -> Part:
    """Return a flak turret: a dome with multiple short barrels."""
    part = Part()
    r = max(1, size // 2)
    part.dome(0, float(r), 0, "N")
    for i in range(4):
        bx = round(r * 0.7 * (1 if i < 2 else -1))
        bz = round(r * 0.7 * (1 if i % 2 == 0 else -1))
        for step in range(size):
            part.put(bx, step, bz, "r" if step == size - 1 else "h")
        part.weapon("flak", bx, size - 1, bz)
    return part


def _cockpit(_rng: object, size: int) -> Part:
    """Return a cockpit: a detailed canopy with frame and glass."""
    part = Part()
    r = max(1, size // 2)
    part.housing(r + 1, 0, size, 0, r)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    if step == size - 1:
                        part.put(dx, step, dz, "S")
                    elif step == 0:
                        part.put(dx, step, dz, "k")
                    else:
                        part.put(dx, step, dz, "H" if abs(dx) == r or dz == 0 else "h")
    return part


def _bridge(_rng: object, size: int) -> Part:
    """Return a command bridge: a raised structure with windows."""
    part = Part()
    r = max(1, size // 2)
    part.housing(r + 1, 0, size, 0, r)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    if step == size - 1:
                        part.put(dx, step, dz, "S")
                    elif step == size - 2:
                        part.put(dx, step, dz, "p")
                    else:
                        part.put(dx, step, dz, "H")
    return part


def _hangar(_rng: object, size: int) -> Part:
    """Return a hangar bay: a recessed bay with doors."""
    part = Part()
    r = max(1, size // 2)
    part.housing(r + 1, 0, size, 0, r)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    if step == 0 or step == size - 1:
                        part.put(dx, step, dz, "k")
                    elif abs(dx) == r:
                        part.put(dx, step, dz, "N")
                    else:
                        part.put(dx, step, dz, "h")
    return part


def _spine(_rng: object, size: int) -> Part:
    """Return a spine: a raised ridge with details."""
    part = Part()
    r = max(1, size // 3)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(r + 1):
                if dx * dx + dz * dz <= r * r + r:
                    part.put(dx, step, dz, "H" if dz == r else "h")
    return part


def _fin(_rng: object, size: int) -> Part:
    """Return a fin: a vertical stabilizer with markings."""
    part = Part()
    r = max(1, size // 2)
    for step in range(size):
        w = r - step // 2
        for x in range(-w, w + 1):
            part.put(x, step, 0, "w" if step < size - 1 else "W")
    return part


def _intake(_rng: object, size: int) -> Part:
    """Return an intake: a recessed opening with a dark interior."""
    part = Part()
    r = max(1, size // 2)
    for step in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    if step == 0:
                        part.put(dx, step, dz, "k")
                    elif abs(dx) == r or abs(dz) == r:
                        part.put(dx, step, dz, "N")
                    else:
                        part.put(dx, step, dz, "h")
    return part


def _exhaust(_rng: object, size: int) -> Part:
    """Return an exhaust port: a glowing port with a dark rim."""
    part = Part()
    r = max(1, size // 2)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                part.put(dx, 0, dz, "o" if dx * dx + dz * dz <= (r - 1) * (r - 1) else "N")
    part.nozzle(0, 0, 0, float(r))
    return part


def _armor_plate(_rng: object, size: int) -> Part:
    """Return an armor plate: raised plating with seams and lights."""
    part = Part()
    r = max(1, size // 2)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                part.put(dx, 0, dz, "N" if (dx + dz) % 2 == 0 else "H")
    for dx in range(-r, r + 1):
        part.put(dx, 0, r, "k")
    for dz in range(-r, r + 1):
        part.put(r, 0, dz, "k")
    part.put(r, 0, r, "p")
    return part


def _panel(_rng: object, size: int) -> Part:
    """Return a detailed panel: a plate with seams, lights, and vents."""
    part = Part()
    r = max(1, size // 2)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                part.put(dx, 0, dz, "h")
    for dx in range(-r, r + 1):
        part.put(dx, 0, 0, "k")
    for dz in range(-r, r + 1):
        part.put(0, 0, dz, "k")
    part.put(r, 0, r, "p")
    part.put(-r, 0, r, "p")
    return part


def _antenna_array(_rng: object, size: int) -> Part:
    """Return an antenna array: multiple antennas with tips."""
    part = Part()
    r = max(1, size // 2)
    for i in range(4):
        ax = round(r * 0.6 * (1 if i < 2 else -1))
        for z in range(size + 1):
            part.put(ax, 0, z, "h")
        part.put(ax, 0, size + 1, "p")
    return part


def _canard(_rng: object, size: int) -> Part:
    """Return a canard: small forward wings."""
    part = Part()
    r = max(1, size // 2)
    for y in range(r + 1):
        w = r - y // 2
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


def _tailplane(_rng: object, size: int) -> Part:
    """Return a tailplane: horizontal stabilizers."""
    part = Part()
    r = max(1, size // 2)
    for y in range(r + 1):
        w = r - y // 2
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


def _swept_wing(_rng: object, size: int) -> Part:
    """Return a swept wing: a wing with swept-back leading edge."""
    part = Part()
    chord = max(3, size * 2)
    span = max(2, size)
    for y in range(chord):
        w = span - y // 3
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


def _delta_wing(_rng: object, size: int) -> Part:
    """Return a delta wing: a triangular wing shape."""
    part = Part()
    chord = max(3, size * 2)
    for y in range(chord):
        w = (chord - y) * 2
        for x in range(-w, w + 1):
            part.put(x, y, 0, "w")
    return part


def _ion_engine(_rng: object, size: int) -> Part:
    """Return an ion engine: a glowing engine with coils."""
    part = Part()
    r = max(1, size)
    for z in range(r + 1):
        rad = r - z + 1
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if dx * dx + dz * dz <= rad * rad:
                    part.put(dx, 0, z, "N" if z == 0 else "h")
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                part.put(dx, 0, 0, "G")
    part.nozzle(0, 0, 0, float(r))
    return part


def _nacelle(_rng: object, size: int) -> Part:
    """Return a nacelle: a wing-mounted engine housing."""
    part = Part()
    r = max(1, size // 2)
    for y in range(size):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    part.put(dx, y, dz, "N" if y == 0 else "h")
    part.nozzle(0, 0, 0, float(r))
    return part


def _thruster(_rng: object, size: int) -> Part:
    """Return a thruster: a small directional maneuvering thruster."""
    part = Part()
    r = max(1, size // 3)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                part.put(dx, 0, dz, "o")
    part.nozzle(0, 0, 0, float(r))
    return part


# Register all parts
register("cube", _cube, tags=[HULL])
register("nose_gun", _nose_gun, tags=[WEAPON, GUN])
register("turret", _turret, tags=[WEAPON, GUN])
register("twin_cannon", _twin_cannon, tags=[WEAPON, GUN])
register("gatling", _gatling, tags=[WEAPON, GUN])
register("flak_gun", _flak_gun, tags=[WEAPON, GUN])
register("beam_emitter", _beam_emitter, tags=[WEAPON, GUN])
register("heavy_cannon", _heavy_cannon, tags=[WEAPON, GUN])
register("plasma_gun", _plasma_gun, tags=[WEAPON, GUN])
register("railgun", _railgun, tags=[WEAPON, GUN])
register("missile_pod", _missile_pod, tags=[WEAPON, MISSILE])
register("flak_turret", _flak_turret, tags=[WEAPON, GUN])
register("missile_rack", _missile_rack, tags=[WEAPON, MISSILE])
register("tail_engine", _tail_engine, tags=[ENGINE])
register("big_engine", _big_engine, tags=[ENGINE])
register("exhaust_stacks", _exhaust_stacks, tags=[ENGINE])
register("ion_engine", _ion_engine, tags=[ENGINE])
register("nacelle", _nacelle, tags=[ENGINE])
register("thruster", _thruster, tags=[ENGINE])
register("wing_root", _wing_root, tags=[WING, STORES])
register("big_wing", _big_wing, tags=[WING, STORES])
register("flying_wing", _flying_wing, tags=[WING, STORES])
register("canard", _canard, tags=[WING])
register("tailplane", _tailplane, tags=[WING])
register("swept_wing", _swept_wing, tags=[WING])
register("delta_wing", _delta_wing, tags=[WING])
register("reactor", _reactor, tags=[POWER])
register("radar", _radar, tags=[SENSOR])
register("antenna", _antenna, tags=[SENSOR])
register("sensor_dome", _sensor_dome, tags=[SENSOR])
register("antenna_array", _antenna_array, tags=[SENSOR])
register("vent", _vent, tags=[VENT])
register("radiator", _radiator, tags=[VENT])
register("fuel_tank", _fuel_tank, tags=[STORES])
register("cockpit", _cockpit, tags=[COCKPIT])
register("bridge", _bridge, tags=[COCKPIT])
register("hangar", _hangar, tags=[HULL])
register("spine", _spine, tags=[HULL])
register("fin", _fin, tags=[HULL])
register("intake", _intake, tags=[VENT])
register("exhaust", _exhaust, tags=[VENT])
register("armor_plate", _armor_plate, tags=[PLATING])
register("panel", _panel, tags=[PLATING])


# ---- Convenience ----


def get_part(name: str, rng: object, size: int = 3) -> Part:
    """Build a part by name `size` big, using `rng` for randomness."""
    if name not in PARTS:
        msg = f"unknown part: {name}"
        raise ValueError(msg)
    return PARTS[name](rng, size)


PART_NAMES = sorted(PARTS.keys())
