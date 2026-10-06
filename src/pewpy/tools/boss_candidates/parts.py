"""A boss's destructible parts: small ships of their own, assembled from the enemies' kit, standing on its hull.

Each kind of part is a recipe like an enemy's (PARTS): a short hull and what's on it, sized to its boss (`scale`).
Its weapons are all of its kind's (PART_WEAPONS: the game's descriptions pick weapons by kind); a part without any is
a target only (a radar, a generator). `mount` picks where the parts go on the core's top, mirrored on a symmetric
boss; `stand` lifts a part so its lowest cubes are just above the core's highest under it, and `socket` paints a
plate on the core under it.
"""

from collections.abc import Callable
from dataclasses import replace

from pewpy.tools.candidates.kit import extras, weapons
from pewpy.tools.candidates.kit.archetypes import wing_pair
from pewpy.tools.candidates.kit.cockpits import COCKPITS
from pewpy.tools.candidates.kit.hulls import Hull, hull
from pewpy.tools.candidates.kit.ship import Ship
from pewpy.tools.common.geometry import Rng

PART_WEAPONS = {  # a part's kind: its weapons' kind ("": none)
    "turret": "turret",
    "cannon": "cannon",
    "gatling": "gatling",
    "flak": "flak",
    "launcher": "missile",
    "emitter": "laser",
    "radar": "",
    "generator": "",
}
PARTS_BY_SIZE = {"medium": (0, 4), "large": (2, 7), "huge": (3, 10)}  # how many parts, by the boss's size class
HULL_TOPS = "hHSNkLWw"  # the core's cubes a part can stand on (not its cockpit, engines or weapons)
MARGIN = 3  # cubes at least from the axis to a mirrored part's middle


def _body(rng: Rng, ship: Ship, names: list[str], scale: float, length: tuple[float, float]) -> Hull:
    return hull(rng, ship, rng.choice(names), round(rng.uniform(*length) * scale), rng.uniform(2.2, 3.4) * scale,
                rng.uniform(1.3, 2.0) * scale)  # fmt: skip


def turret(rng: Rng, scale: float) -> Ship:
    """Build a turret: a squat hull, a turret on top (two barrels), guns in its nose sometimes."""
    ship = Ship()
    body = _body(rng, ship, ["bulb", "brick"], scale, (6, 9))
    weapons.turret(rng, ship, body, body.length // 2)
    if rng.random() < 0.4:
        weapons.nose_guns(rng, ship, body)
    return ship


def cannon(rng: Rng, scale: float) -> Ship:
    """Build a cannon: a long housing, guns out of its nose, armor on its sides."""
    ship = Ship()
    body = _body(rng, ship, ["brick", "wedge", "cigar"], scale, (8, 12))
    weapons.nose_guns(rng, ship, body)
    extras.armor(rng, ship, body)
    return ship


def gatling(rng: Rng, scale: float) -> Ship:
    """Build a gatling mount: a round housing, a gatling under its nose."""
    ship = Ship()
    body = _body(rng, ship, ["bulb", "cigar"], scale, (7, 10))
    weapons.gatling(rng, ship, body)
    return ship


def flak(rng: Rng, scale: float) -> Ship:
    """Build a flak battery: a blocky housing, stubby sponsons, a gun on each."""
    ship = Ship()
    body = _body(rng, ship, ["brick", "hammer"], scale, (6, 9))
    sponson = wing_pair(rng, ship, body, "box", trailing=(0.3, 0.4), chord=(0.3, 0.4), span=(1, 2), rise=0.0, char="h")
    weapons.wing_guns(rng, ship, sponson, 0.9)
    return ship


def launcher(rng: Rng, scale: float) -> Ship:
    """Build a missile launcher: a housing, stubby racks with missiles under them and on their tips."""
    ship = Ship()
    body = _body(rng, ship, ["brick", "wedge"], scale, (7, 10))
    rack = wing_pair(rng, ship, body, rng.choice(["box", "trapezoid"]), trailing=(0.2, 0.3), chord=(0.4, 0.5),
                     span=(2, 4), rise=0.0)  # fmt: skip
    weapons.missiles(rng, ship, rack)
    weapons.tip_weapons(rng, ship, rack)
    return ship


def emitter(rng: Rng, scale: float) -> Ship:
    """Build a beam emitter: a slim housing, a glowing eye on its nose, a barrel through it, fins."""
    ship = Ship()
    body = _body(rng, ship, ["spindle", "needle"], scale, (8, 12))
    weapons.nose_guns(rng, ship, body)
    COCKPITS["eye"](rng, ship, body)
    extras.fins(rng, ship, body)
    return ship


def radar(rng: Rng, scale: float) -> Ship:
    """Build a radar: a small housing, a dome and a mast."""
    ship = Ship()
    body = _body(rng, ship, ["bulb", "brick"], scale, (6, 8))
    extras.dome(rng, ship, body)
    extras.antenna(rng, ship, body)
    return ship


def generator(rng: Rng, scale: float) -> Ship:
    """Build a generator: a round housing, its top glowing, a dome."""
    ship = Ship()
    body = _body(rng, ship, ["bulb", "spindle", "cigar"], scale, (7, 10))
    tops = ship.tops()
    for (x, y, z), char in list(ship.cells.items()):
        if char in "hH" and z == tops[x, y] and abs(x) <= 1:
            ship.cells[x, y, z] = "G"
    extras.dome(rng, ship, body)
    return ship


PARTS: dict[str, Callable[[Rng, float], Ship]] = {
    "turret": turret,
    "cannon": cannon,
    "gatling": gatling,
    "flak": flak,
    "launcher": launcher,
    "emitter": emitter,
    "radar": radar,
    "generator": generator,
}


def part(rng: Rng, kind: str, scale: float) -> Ship:
    """Build a part of a kind, its weapons all of the kind's (none for a target only)."""
    ship = PARTS[kind](rng, scale)
    weapon = PART_WEAPONS[kind]
    ship.weapons = [replace(w, kind=weapon) for w in ship.weapons] if weapon else []
    return ship


Mount = tuple[str, int, int, bool]  # (kind, x, y, mirrored too): x across (<= 0, left of the axis), y from the tail


def mount(rng: Rng, core: Ship, symmetric: bool, size: str) -> list[Mount]:
    """Pick where the parts go on the core's top: a few kinds, spread out, mirrored on a symmetric boss."""
    low, high = PARTS_BY_SIZE[size]
    wanted = rng.randint(low, high)
    kinds = rng.sample(list(PARTS), rng.randint(1, 3))  # a boss uses a few kinds of parts, not all of them
    width, _ = core.size()
    tops = core.tops()
    hull_tops = {(x, y) for (x, y), z in tops.items() if core.cells[x, y, z] in HULL_TOPS}
    inner = {
        (x, y) for x, y in hull_tops if all(n in hull_tops for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    }
    spots = sorted((x, y) for x, y in inner if x <= -MARGIN)  # inside the hull, not on its outline
    spacing = max(8, width // 8)
    mounts: list[Mount] = []
    placed = 0
    while placed < wanted and spots:
        x, y = rng.choice(spots)
        mirrored = symmetric or rng.random() < 0.5
        mounts.append((rng.choice(kinds), x, y, mirrored))
        placed += 2 if mirrored else 1
        spots = [(sx, sy) for sx, sy in spots if abs(sx - x) > spacing or abs(sy - y) > spacing]
    middle = sorted(y for x, y in inner if x == 0)
    if middle and rng.random() < 0.35:  # something on the axis
        mounts.append((rng.choice(kinds), 0, rng.choice(middle), False))
    return mounts


def stand(core: Ship, piece: Ship, x: int, y: int) -> tuple[Ship, float, float]:
    """Place a part with its middle at (x, y) on the core, standing on it; return it moved there, and its middle.

    Its lowest cubes are just above the core's highest under it.
    """
    xs, ys = [cx for cx, _, _ in piece.cells], [cy for _, cy, _ in piece.cells]
    dx, dy = x - round((min(xs) + max(xs)) / 2), y - round((min(ys) + max(ys)) / 2)
    tops = core.tops()
    under = [tops[cx + dx, cy + dy] for cx, cy, _ in piece.cells if (cx + dx, cy + dy) in tops]
    lift = max(under, default=0) + 1 - min(z for _, _, z in piece.cells)
    moved = Ship({(cx + dx, cy + dy, z + lift): char for (cx, cy, z), char in piece.cells.items()},
                 weapons=[replace(w, x=w.x + dx, y=w.y + dy, z=w.z + lift) for w in piece.weapons],
                 symmetric=piece.symmetric)  # fmt: skip
    return moved, (min(xs) + max(xs)) / 2 + dx, (min(ys) + max(ys)) / 2 + dy


def socket(core: Ship, piece: Ship) -> None:
    """Paint a plate on the core's top under a placed part, a cube wider all round: the part stands out over it."""
    tops = core.tops()
    under = {(x + ax, y + ay) for x, y, _ in piece.cells for ax in (-1, 0, 1) for ay in (-1, 0, 1)}
    for x, y in under:
        if (x, y) in tops and core.cells[x, y, tops[x, y]] in HULL_TOPS:
            core.cells[x, y, tops[x, y]] = "N"
