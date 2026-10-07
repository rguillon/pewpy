"""The kinds of ship, each a recipe placing parts from the kit.

A recipe says which hulls, wings, cockpits, engines, weapons and extras it picks among, and where they go.
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from pewpy.makers.common.geometry import Rng
from pewpy.makers.ships.kit import extras, weapons
from pewpy.makers.ships.kit.cockpits import COCKPITS
from pewpy.makers.ships.kit.engines import nacelle, tail_engines
from pewpy.makers.ships.kit.hulls import Hull, hull
from pewpy.makers.ships.kit.ship import Ship
from pewpy.makers.ships.kit.wings import Wing, wing

MAX_HALF = 17  # cubes from the axis to a wing tip: ships stay at most 35 wide (at a fit of 1, see Ship)
PLAYER_MAX_HALF = 21  # the player's ships' recipes, written for cubes half the size (see PLAYER_FIT): at most 43 wide


def fighter(rng: Rng, fit: float = 1.0) -> Ship:
    """Build a fighter: a slim hull, swept or delta wings, a tailplane or canards, a canopy, guns, fins."""
    ship = Ship(fit=fit)
    body = hull(
        rng,
        ship,
        rng.choice(["dart", "shark", "cigar"]),
        rng.randint(11, 22),
        rng.uniform(1.5, 2.4),
        rng.uniform(1.2, 2.0),
    )
    main = _wings(
        rng,
        ship,
        body,
        rng.choice(["swept", "delta", "cranked", "ogival", "forward", "scythe"]),
        trailing=(0.12, 0.3),
        chord=(0.3, 0.45),
        span=(4, 10),
        rise=rng.choice([0.0, 0.1, 0.2]),
    )
    if rng.random() < 0.6:
        _tailplane(rng, ship, body)
    else:
        _canards(rng, ship, body)
    COCKPITS[rng.choice(["bubble", "bubble", "canopy"])](rng, ship, body)
    _guns(rng, ship, body, main)
    tail_engines(ship, body, rng.choice([1, 2]), rng.choice([1, 2]))
    extras.fins(rng, ship, body)
    _sometimes(rng, ship, body, {extras.intakes: 0.4, extras.antenna: 0.2})
    _finish(rng, ship, body)
    return ship


def interceptor(rng: Rng, fit: float = 1.0) -> Ship:
    """Build an interceptor: long and thin, small forward-swept or delta wings, canards, tip guns, twin engines."""
    ship = Ship(fit=fit)
    body = hull(
        rng,
        ship,
        rng.choice(["spindle", "cigar", "dart"]),
        rng.randint(16, 26),
        rng.uniform(1.0, 1.6),
        rng.uniform(1.0, 1.6),
    )
    main = _wings(
        rng,
        ship,
        body,
        rng.choice(["forward", "delta", "scythe", "trapezoid"]),
        trailing=(0.08, 0.2),
        chord=(0.22, 0.32),
        span=(3, 7),
        rise=0.0,
    )
    _canards(rng, ship, body)
    COCKPITS["canopy"](rng, ship, body)
    weapons.tip_weapons(rng, ship, main)
    if rng.random() < 0.5:
        weapons.nose_guns(rng, ship, body)
    tail_engines(ship, body, 2, 1)
    extras.fins(rng, ship, body)
    _finish(rng, ship, body)
    return ship


def bomber(rng: Rng, fit: float = 1.0) -> Ship:
    """Build a bomber: a wide hull, long straight wings with engine pods under them, a turret, missiles, twin fins."""
    ship = Ship(fit=fit)
    body = hull(
        rng,
        ship,
        rng.choice(["cigar", "brick", "shark"]),
        rng.randint(14, 24),
        rng.uniform(2.2, 3.4),
        rng.uniform(1.6, 2.4),
    )
    main = _wings(
        rng,
        ship,
        body,
        rng.choice(["straight", "trapezoid", "swept", "bat"]),
        trailing=(0.3, 0.45),
        chord=(0.22, 0.32),
        span=(8, 13),
        rise=rng.choice([0.0, 0.08]),
    )
    xs = sorted(main.leading)  # from the tip in
    for share in rng.choice([[0.5], [0.5], [0.3, 0.7]]):
        x = xs[min(len(xs) - 1, round(share * (len(xs) - 1)))]
        front, z = main.leading[x]
        nacelle(ship, x, z - 2, front - rng.randint(4, 6), rng.randint(5, 7))
    _tailplane(rng, ship, body)
    COCKPITS[rng.choice(["bubble", "visor", "bridge"])](rng, ship, body)
    weapons.turret(rng, ship, body, round(body.length * 0.4))
    if rng.random() < 0.6:
        weapons.missiles(rng, ship, main)
    if rng.random() < 0.5:
        weapons.nose_guns(rng, ship, body)
    if rng.random() < 0.4:
        tail_engines(ship, body, 1, 2)
    extras.fins(rng, ship, body)
    _finish(rng, ship, body)
    return ship


def drone(rng: Rng, fit: float = 1.0) -> Ship:
    """Build a drone: small and round, stubby wings or side pods, a sensor eye, a gun, one engine, an antenna."""
    ship = Ship(fit=fit)
    body = hull(
        rng,
        ship,
        rng.choice(["bulb", "spindle", "cigar"]),
        rng.randint(7, 12),
        rng.uniform(1.6, 2.4),
        rng.uniform(1.0, 1.8),
    )
    if rng.random() < 0.25:  # no wings: engine pods on its sides
        y = body.widest()
        nacelle(ship, -round(body.half(y)) - 1, 0, max(0, y - 3), rng.randint(3, 5), size=1)
    else:
        main = _wings(
            rng,
            ship,
            body,
            rng.choice(["box", "bat", "trapezoid", "swept"]),
            trailing=(0.2, 0.35),
            chord=(0.3, 0.45),
            span=(2, 5),
            rise=rng.choice([0.0, 0.3, -0.3]),
        )
        if rng.random() < 0.5:
            weapons.tip_weapons(rng, ship, main)
    COCKPITS["eye"](rng, ship, body)
    if rng.random() < 0.6:
        weapons.nose_guns(rng, ship, body)
    else:
        weapons.gatling(rng, ship, body)
    tail_engines(ship, body, 1, rng.choice([1, 2]), depth=1)
    _sometimes(rng, ship, body, {extras.antenna: 0.6, extras.dome: 0.3})
    _finish(rng, ship, body)
    return ship


def gunship(rng: Rng, fit: float = 1.0) -> Ship:
    """Build a gunship: a blocky hull, sponsons with guns, a gatling, armor, a bridge or visor, two or three engines."""
    ship = Ship(fit=fit)
    body = hull(
        rng,
        ship,
        rng.choice(["brick", "hammer", "wedge"]),
        rng.randint(12, 22),
        rng.uniform(2.4, 3.8),
        rng.uniform(1.6, 2.6),
    )
    if rng.random() < 0.7:
        sponson = _wings(
            rng,
            ship,
            body,
            rng.choice(["box", "trapezoid"]),
            trailing=(0.35, 0.5),
            chord=(0.2, 0.3),
            span=(2, 4),
            rise=0.0,
            char="h",
        )
        weapons.wing_guns(rng, ship, sponson, 0.9)
    if rng.random() < 0.6:
        weapons.gatling(rng, ship, body)
    else:
        weapons.nose_guns(rng, ship, body)
    COCKPITS[rng.choice(["bridge", "visor"])](rng, ship, body)
    tail_engines(ship, body, rng.choice([2, 3]), 2)
    extras.armor(rng, ship, body)
    _sometimes(rng, ship, body, {extras.antenna: 0.6, extras.fins: 0.4, extras.dome: 0.2})
    if rng.random() < 0.3:
        weapons.side_cannon(rng, ship, body)
    _finish(rng, ship, body)
    return ship


def heavy(rng: Rng, fit: float = 1.0) -> Ship:
    """Build a heavy: a big hull, short wings with engine pods on their tips, turrets, a bridge, armor, big engines."""
    ship = Ship(fit=fit)
    body = hull(
        rng,
        ship,
        rng.choice(["wedge", "brick", "hammer", "shark"]),
        rng.randint(18, 30),
        rng.uniform(3.5, 5.5),
        rng.uniform(2.0, 3.0),
    )
    main = _wings(
        rng,
        ship,
        body,
        rng.choice(["box", "trapezoid", "swept", "delta"]),
        trailing=(0.15, 0.3),
        chord=(0.25, 0.4),
        span=(3, 7),
        rise=0.0,
    )
    if main.tip:
        x, y, z = main.tip[0]
        nacelle(ship, x, z, y - 1, rng.randint(6, 9), size=rng.choice([2, 3]))
    for share in (0.35, 0.65)[: rng.randint(1, 2)]:
        weapons.turret(rng, ship, body, round(body.length * share))
    COCKPITS["bridge"](rng, ship, body)
    tail_engines(ship, body, 3, rng.choice([2, 3]))
    extras.armor(rng, ship, body)
    _sometimes(rng, ship, body, {extras.fins: 0.6, extras.dome: 0.4, extras.antenna: 0.5})
    if rng.random() < 0.5:
        weapons.nose_guns(rng, ship, body)
    _finish(rng, ship, body)
    return ship


Archetype = Callable[..., Ship]  # (rng, fit=1.0) -> a ship of the kind
ARCHETYPES: dict[str, Archetype] = {
    "fighter": fighter,
    "interceptor": interceptor,
    "bomber": bomber,
    "drone": drone,
    "gunship": gunship,
    "heavy": heavy,
}


# The player's ships, in the spirit of the game's three (01-gameplay.md, "Ships"), their recipes written for cubes half
# the size (made at PLAYER_FIT, they're the size of the game's ships). A ship's class sets its size; its layout,
# engines, cockpit, weapons, extras and paint are picked each on their own.

PLAYER_CLASSES = {  # (length, half width, height, wing span, engine size, hulls)
    "vanguard": ((30, 38), (3.0, 4.5), (2.2, 3.2), (9, 14), 3, ["dart", "shark", "cigar", "needle", "arrow"]),
    "juggernaut": ((34, 42), (5.0, 7.0), (3.0, 4.0), (6, 11), 3, ["wedge", "brick", "shark", "hammer", "manta"]),
    "phantom": ((28, 34), (2.0, 3.0), (1.8, 2.6), (8, 13), 2, ["spindle", "dart", "needle", "cigar", "arrow"]),
}
PLAYER_FIT = 0.5
EQUIPMENT_CHANCE = 0.6  # of a ship carrying built-in parts (see extras.equipment)
PLAYER_LAYOUTS = ["single", "single", "single", "x_wing", "biplane", "tandem", "flying_wing", "twin_boom"]
ALL_OUTLINES = ["swept", "delta", "forward", "straight", "cranked", "ogival", "bat", "trapezoid", "scythe", "box"]


@dataclass
class Frame:
    """What a player's ship is made of so far: its hull, its main wings, its booms' places (if any)."""

    body: Hull
    main: Wing
    booms: list[tuple[int, int, int]]  # (x from the axis, its tail's row, its length): on the left, mirrored


def player_ship(rng: Rng, kind: str, fit: float = 1.0) -> Ship:
    """Build a player's ship of a class (PLAYER_CLASSES), its layout and everything on it picked at random.

    `fit`: how much bigger than the class's own size it is made (see Ship).
    """
    lengths, halves, heights, span, engine, hulls = PLAYER_CLASSES[kind]
    engine = max(1, round(engine * fit / PLAYER_FIT / 2))  # nozzles as wide as the ship's cubes allow
    ship = Ship(fit=fit)
    layout = rng.choice(PLAYER_LAYOUTS)
    name = rng.choice(["manta", "spindle", "arrow"]) if layout == "flying_wing" else rng.choice(hulls)
    length = rng.randint(*lengths) - (6 if layout == "flying_wing" else 0)
    body = hull(rng, ship, name, length, rng.uniform(*halves), rng.uniform(*heights))
    frame = _player_wings(rng, ship, body, layout, span)
    if layout in ("single", "twin_boom") and rng.random() < 0.6:
        (_tailplane if rng.random() < 0.5 else _canards)(rng, ship, body)
    cockpits = ["bubble", "bubble", "canopy", "visor"] + (["bridge"] if kind == "juggernaut" else [])
    COCKPITS[rng.choice(cockpits)](rng, ship, body)
    _player_engines(rng, ship, frame, engine)
    _player_weapons(rng, ship, frame, kind)
    extras_chances: dict[Callable[[Rng, Ship, Hull], None], float] = {
        extras.fins: 0.5 if layout == "flying_wing" else 0.75,
        extras.intakes: 0.45,
        extras.antenna: 0.25,
        extras.armor: 0.7 if kind == "juggernaut" else 0.15,
        extras.dome: 0.1,
        extras.equipment: EQUIPMENT_CHANCE,
    }
    _sometimes(rng, ship, body, extras_chances)
    _player_paint(rng, ship, body)
    if not ship.weapons:
        weapons.nose_guns(rng, ship, body)
    return ship


def _player_wings(rng: Rng, ship: Ship, body: Hull, layout: str, span: tuple[int, int]) -> Frame:
    """Put the wings of a layout.

    One pair, crossed pairs, stacked pairs, two pairs one behind the other, a flying wing, or a pair carrying two booms.
    """
    outline = rng.choice(ALL_OUTLINES)
    rise = rng.choice([0.0, 0.0, 0.08, 0.15, -0.1])
    booms: list[tuple[int, int, int]] = []
    if layout == "x_wing":  # two pairs, one rising and one drooping: an X seen from behind
        outline = rng.choice(["box", "trapezoid", "straight", "swept"])
        main = _wings(
            rng, ship, body, outline, (0.1, 0.2), (0.25, 0.35), span, 0.3, z_shift=1, max_half=PLAYER_MAX_HALF
        )
        _wings(rng, ship, body, outline, (0.1, 0.2), (0.25, 0.35), span, -0.3, z_shift=-1, max_half=PLAYER_MAX_HALF)
    elif layout == "biplane":  # two pairs, one above the other
        main = _wings(
            rng, ship, body, outline, (0.2, 0.3), (0.25, 0.35), span, 0.0, z_shift=2, max_half=PLAYER_MAX_HALF
        )
        _wings(rng, ship, body, outline, (0.15, 0.25), (0.25, 0.35), span, 0.0, z_shift=-2, max_half=PLAYER_MAX_HALF)
    elif layout == "tandem":  # a small pair forward, the main pair at the back
        main = _wings(rng, ship, body, outline, (0.05, 0.15), (0.25, 0.35), span, rise, max_half=PLAYER_MAX_HALF)
        small = (max(3, span[0] // 2), max(4, span[1] // 2))
        _wings(
            rng, ship, body, rng.choice(ALL_OUTLINES), (0.55, 0.65), (0.15, 0.22), small, rise, max_half=PLAYER_MAX_HALF
        )
    elif layout == "flying_wing":  # one wide wing, most of the ship
        outline = rng.choice(["delta", "bat", "ogival", "cranked", "scythe"])
        wide = (span[0] + 2, span[1] + 4)
        main = _wings(
            rng, ship, body, outline, (0.0, 0.08), (0.6, 0.8), wide, rng.choice([0.0, 0.05]), max_half=PLAYER_MAX_HALF
        )
    else:
        main = _wings(rng, ship, body, outline, (0.1, 0.3), (0.3, 0.45), span, rise, max_half=PLAYER_MAX_HALF)
    if layout == "twin_boom" and main.leading:
        xs = sorted(main.leading)
        x = xs[len(xs) // 2]  # halfway out along the wing
        front, z = main.leading[x]
        long = round(body.length * rng.uniform(0.55, 0.75))
        tail = max(0, front + 4 - long)
        hull(rng, ship, rng.choice(["cigar", "spindle"]), long, rng.uniform(1.5, 2.2), rng.uniform(1.5, 2.0),
             offset=-x, back=tail)  # fmt: skip
        booms.append((x, tail, long))
        for y in range(tail, tail + 4):  # a fin on each boom's tail
            for dz in range(1, 4 - (y - tail) // 2 + 1):
                ship.put(x, y, z + 1 + dz, "S")
    return Frame(body, main, booms)


def _player_engines(rng: Rng, ship: Ship, frame: Frame, size: int) -> None:
    """Put the engines: at the tail, at the booms' tails, in pods on the wings, or in pods on the hull's sides."""
    body = frame.body
    if frame.booms:
        for x, tail, _ in frame.booms:
            nacelle(ship, x, 0, tail - 2, 4, size=min(size, 2))
        if rng.random() < 0.5:
            tail_engines(ship, body, 1, size, depth=3)
        return
    layout = rng.choice(["tail", "tail", "tail", "wing_pods", "side_pods"])
    if layout == "wing_pods" and frame.main.leading:
        xs = sorted(frame.main.leading)
        x = xs[len(xs) // 2]
        front, z = frame.main.leading[x]
        nacelle(ship, x, z - 2, front - ship.fitted(rng.randint(8, 12)), rng.randint(9, 13), size=min(size, 3))
        if rng.random() < 0.5:
            tail_engines(ship, body, 1, size, depth=3)
        return
    if layout == "side_pods":
        y = round(body.length * 0.3)
        nacelle(ship, -round(body.half(y)) - 2, 0, 0, round(body.length * rng.uniform(0.35, 0.5)), size=2)
        if rng.random() < 0.6:
            tail_engines(ship, body, 1, size, depth=3)
        return
    tail_engines(ship, body, rng.choice([1, 2, 2, 3]), size, depth=rng.randint(2, 4))


def _player_weapons(rng: Rng, ship: Ship, frame: Frame, kind: str) -> None:
    """Arm it: one to three of nose guns, wing guns, tip guns or missiles, missiles under the wings, a turret."""
    choices = [
        lambda: weapons.nose_guns(rng, ship, frame.body),
        lambda: weapons.wing_guns(rng, ship, frame.main, rng.uniform(0.3, 0.7)),
        lambda: weapons.tip_weapons(rng, ship, frame.main),
        lambda: weapons.missiles(rng, ship, frame.main),
    ]
    if kind == "juggernaut":
        choices.append(lambda: weapons.turret(rng, ship, frame.body, round(frame.body.length * 0.45)))
    for arm in rng.sample(choices, rng.randint(1, 3)):
        arm()


def _player_paint(rng: Rng, ship: Ship, body: Hull) -> None:
    """Paint its bits, its main color staying its greys.

    Plain, a livery stripe, a nose cone or wing stripes (or two of them), and markings.
    """
    schemes = [
        lambda: None,
        lambda: extras.livery(rng, ship, body),
        lambda: extras.nose_cone(rng, ship, body),
        lambda: extras.wing_stripes(rng, ship),
    ]
    for scheme in rng.sample(schemes, rng.choice([1, 1, 2])):
        scheme()
    if rng.random() < 0.6:
        extras.markings(rng, ship)


PLAYER_ARCHETYPES: dict[str, Archetype] = {kind: partial(player_ship, kind=kind) for kind in PLAYER_CLASSES}


def _wings(
    rng: Rng,
    ship: Ship,
    body: Hull,
    outline: str,
    trailing: tuple[float, float],
    chord: tuple[float, float],
    span: tuple[int, int],
    rise: float,
    char: str = "w",
    max_half: int = MAX_HALF,
    z_shift: int | None = None,
) -> Wing:
    """Put a pair of wings on the hull's sides: their trailing edge and chord as shares of its length.

    Their tips at most `max_half` cubes from the axis; their root `z_shift` cubes above the hull's middle (by default,
    the middle or a cube off it).
    """
    back = round(body.length * rng.uniform(*trailing))
    long = max(2, round(body.length * rng.uniform(*chord)))
    rows = list(range(back, min(body.length, back + long))) or [back]
    root = -max(1, round(min(body.half(y) for y in rows)))
    reach = min(ship.fitted(rng.randint(*span)), ship.fitted(max_half) + root)
    shift = rng.choice([0, 0, 1, -1]) if z_shift is None else z_shift
    z = (body.top_at(back) + body.bottom_at(back)) // 2 + shift
    return wing(ship, outline, root, back, reach, long, z, rise, tip_marking=rng.random() < 0.4, char=char)


def _tailplane(rng: Rng, ship: Ship, body: Hull) -> None:
    """Put a small tailplane at the back."""
    _wings(
        rng,
        ship,
        body,
        rng.choice(["swept", "trapezoid"]),
        trailing=(0.02, 0.05),
        chord=(0.12, 0.18),
        span=(2, 4),
        rise=0.0,
    )


def _canards(rng: Rng, ship: Ship, body: Hull) -> None:
    """Put small canards near the nose."""
    _wings(
        rng,
        ship,
        body,
        rng.choice(["delta", "swept", "trapezoid"]),
        trailing=(0.68, 0.75),
        chord=(0.08, 0.12),
        span=(1, 3),
        rise=0.0,
    )


def _guns(rng: Rng, ship: Ship, body: Hull, main: Wing) -> None:
    """Arm a fighter: guns in the nose, on the wings or their tips, maybe missiles."""
    choice = rng.random()
    if choice < 0.35:
        weapons.nose_guns(rng, ship, body)
    elif choice < 0.7:
        weapons.wing_guns(rng, ship, main, rng.uniform(0.3, 0.6))
    else:
        weapons.tip_weapons(rng, ship, main)
    if rng.random() < 0.35:
        weapons.missiles(rng, ship, main)


def _sometimes(rng: Rng, ship: Ship, body: Hull, chances: dict[Callable[[Rng, Ship, Hull], None], float]) -> None:
    """Put each extra with its chance."""
    for extra, chance in chances.items():
        if rng.random() < chance:
            extra(rng, ship, body)


def _finish(rng: Rng, ship: Ship, body: Hull) -> None:
    """Add equipment, sometimes; make sure it's armed (guns in its nose if nothing else), then paint it."""
    if rng.random() < EQUIPMENT_CHANCE:
        extras.equipment(rng, ship, body)
    if not ship.weapons:
        weapons.nose_guns(rng, ship, body)
    _paint(rng, ship, body)


def _paint(rng: Rng, ship: Ship, body: Hull) -> None:
    """Paint the livery and the markings, sometimes."""
    if rng.random() < 0.55:
        extras.livery(rng, ship, body)
    if rng.random() < 0.6:
        extras.markings(rng, ship)
