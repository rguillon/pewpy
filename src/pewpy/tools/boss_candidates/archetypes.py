"""The kinds of boss, each a recipe placing parts from the enemies' kit (pewpy.tools.candidates.kit), bigger.

Like an enemy's recipe, a boss's says which hulls, wings, cockpits, engines, weapons and extras it picks among and
where they go, its sizes times the boss's `scale` (see SIZES). Its destructible parts are placed on it afterwards
(see parts.py).
"""

from collections.abc import Callable

from pewpy.tools.candidates.kit import extras, weapons
from pewpy.tools.candidates.kit.archetypes import paint, sometimes, wing_pair
from pewpy.tools.candidates.kit.cockpits import COCKPITS
from pewpy.tools.candidates.kit.engines import nacelle, tail_engines
from pewpy.tools.candidates.kit.hulls import Hull, hull
from pewpy.tools.candidates.kit.ship import Ship
from pewpy.tools.common.geometry import Rng

SIZES = {  # by size class: (share of the bosses, scale, cubes from the axis to a wing tip at most)
    "medium": (0.35, 1.0, 30),
    "large": (0.4, 1.35, 42),
    "huge": (0.25, 1.8, 57),
}


def _within(rng: Rng, low: float, high: float, scale: float) -> int:
    """Return a whole number of cubes between `low` and `high`, times `scale`."""
    return round(rng.uniform(low, high) * scale)


def _span(low: float, high: float, scale: float) -> tuple[int, int]:
    return round(low * scale), round(high * scale)


def carrier(rng: Rng, scale: float, reach: int) -> tuple[Ship, Hull]:
    """Build a carrier: a boxy hull, wide flight decks on its sides, a bridge, many engines."""
    ship = Ship()
    body = hull(rng, ship, rng.choice(["brick", "wedge", "hammer"]), _within(rng, 26, 34, scale),
                rng.uniform(8, 10) * scale, rng.uniform(3, 4))  # fmt: skip
    wing_pair(rng, ship, body, rng.choice(["box", "trapezoid"]), trailing=(0.12, 0.25), chord=(0.45, 0.6),
              span=_span(12, 18, scale), rise=0.0, char="h", max_half=reach)  # fmt: skip
    COCKPITS["bridge"](rng, ship, body)
    tail_engines(ship, body, 3, 3, depth=3)
    extras.armor(rng, ship, body)
    sometimes(rng, ship, body, {extras.antenna: 0.7, extras.dome: 0.5, extras.fins: 0.3})
    return ship, body


def dreadnought(rng: Rng, scale: float, reach: int) -> tuple[Ship, Hull]:
    """Build a dreadnought: a long pointed hull, swept wings with engine pods, turrets on the spine, a bridge."""
    ship = Ship()
    body = hull(rng, ship, rng.choice(["wedge", "arrow", "shark", "hammer"]), _within(rng, 30, 38, scale),
                rng.uniform(6, 8) * scale, rng.uniform(3.5, 5))  # fmt: skip
    main = wing_pair(rng, ship, body, rng.choice(["swept", "delta", "cranked", "trapezoid"]), trailing=(0.05, 0.2),
                     chord=(0.3, 0.4), span=_span(14, 20, scale), rise=0.0, max_half=reach)  # fmt: skip
    _pods(rng, ship, main.leading, rng.choice([[0.5], [0.3, 0.7]]), 3)
    for share in (0.3, 0.5, 0.7)[: rng.randint(1, 3)]:
        weapons.turret(rng, ship, body, round(body.length * share))
    COCKPITS["bridge"](rng, ship, body)
    tail_engines(ship, body, 3, 3, depth=3)
    extras.armor(rng, ship, body)
    sometimes(rng, ship, body, {extras.fins: 0.6, extras.antenna: 0.5})
    return ship, body


def flying_wing(rng: Rng, scale: float, reach: int) -> tuple[Ship, Hull]:
    """Build a flying wing: a flat hull inside one huge wing, engine pods along it, a visor or a sensor eye."""
    ship = Ship()
    body = hull(rng, ship, rng.choice(["manta", "arrow", "spindle"]), _within(rng, 26, 34, scale),
                rng.uniform(5, 7) * scale, rng.uniform(2.5, 3.5))  # fmt: skip
    main = wing_pair(rng, ship, body, rng.choice(["delta", "bat", "ogival", "cranked", "scythe"]),
                     trailing=(0.0, 0.08), chord=(0.6, 0.8), span=_span(18, 26, scale), rise=rng.choice([0.0, 0.05]),
                     max_half=reach)  # fmt: skip
    _pods(rng, ship, main.leading, [0.35, 0.7], 2)
    COCKPITS[rng.choice(["visor", "eye"])](rng, ship, body)
    tail_engines(ship, body, rng.choice([1, 2]), 3, depth=3)
    sometimes(rng, ship, body, {extras.dome: 0.4})
    return ship, body


def twin_hull(rng: Rng, scale: float, reach: int) -> tuple[Ship, Hull]:
    """Build a twin hull: a short middle hull, a wide deck joining two long side hulls, engines at their tails."""
    ship = Ship()
    body = hull(rng, ship, rng.choice(["cigar", "brick", "bulb"]), _within(rng, 20, 26, scale),
                rng.uniform(4, 5) * scale, rng.uniform(3, 4))  # fmt: skip
    deck = wing_pair(rng, ship, body, "box", trailing=(0.3, 0.4), chord=(0.3, 0.45), span=_span(16, 22, scale),
                     rise=0.0, char="h", max_half=reach)  # fmt: skip
    xs = sorted(deck.leading)
    if xs:
        x = xs[len(xs) // 4]  # most of the way out
        front, _ = deck.leading[x]
        long = round(body.length * rng.uniform(1.2, 1.5))
        tail = max(0, front + 6 - long)
        side = hull(rng, ship, rng.choice(["cigar", "brick", "dart"]), long, rng.uniform(3, 4.5) * scale,
                    rng.uniform(3, 4), offset=-x, back=tail)  # fmt: skip
        nacelle(ship, x, (side.top_at(0) + side.bottom_at(0)) // 2, tail - 3, 4, size=3)
    COCKPITS["bridge"](rng, ship, body)
    sometimes(rng, ship, body, {extras.antenna: 0.6, extras.dome: 0.4})
    return ship, body


def mothership(rng: Rng, scale: float, reach: int) -> tuple[Ship, Hull]:
    """Build a mothership: a big round hull, short wings, domes and a sensor eye, many engines."""
    ship = Ship()
    body = hull(rng, ship, rng.choice(["bulb", "spindle", "cigar"]), _within(rng, 26, 32, scale),
                rng.uniform(10, 13) * scale, rng.uniform(4, 6))  # fmt: skip
    main = wing_pair(rng, ship, body, rng.choice(["bat", "straight", "trapezoid"]), trailing=(0.3, 0.45),
                     chord=(0.25, 0.35), span=_span(10, 16, scale), rise=rng.choice([0.0, 0.15, -0.15]),
                     max_half=reach)  # fmt: skip
    if main.tip:
        x, y, z = main.tip[0]
        nacelle(ship, x, z, y - 2, _within(rng, 8, 11, scale), size=3)
    COCKPITS["eye"](rng, ship, body)
    extras.dome(rng, ship, body)
    tail_engines(ship, body, 3, 3, depth=3)
    sometimes(rng, ship, body, {extras.antenna: 0.6, extras.intakes: 0.5})
    return ship, body


def gunline(rng: Rng, scale: float, reach: int) -> tuple[Ship, Hull]:
    """Build a gunline: a wide blocky hull, a long gun deck across it, guns along its front, armor."""
    ship = Ship()
    body = hull(rng, ship, rng.choice(["brick", "hammer"]), _within(rng, 24, 30, scale), rng.uniform(8, 10) * scale,
                rng.uniform(3, 4))  # fmt: skip
    deck = wing_pair(rng, ship, body, rng.choice(["box", "straight", "trapezoid"]), trailing=(0.15, 0.3),
                     chord=(0.35, 0.5), span=_span(14, 20, scale), rise=0.0, char="h", max_half=reach)  # fmt: skip
    for share in (0.3, 0.7):
        weapons.wing_guns(rng, ship, deck, share)
    COCKPITS[rng.choice(["bridge", "visor"])](rng, ship, body)
    tail_engines(ship, body, rng.choice([2, 3]), 3, depth=3)
    extras.armor(rng, ship, body)
    sometimes(rng, ship, body, {extras.antenna: 0.5, extras.fins: 0.4})
    return ship, body


def _pods(rng: Rng, ship: Ship, leading: dict[int, tuple[int, int]], shares: list[float], size: int) -> None:
    """Hang engine pods under a wing, at shares of the way from its tip to its root."""
    xs = sorted(leading)  # from the tip in
    for share in shares:
        if xs:
            x = xs[min(len(xs) - 1, round(share * (len(xs) - 1)))]
            front, z = leading[x]
            nacelle(ship, x, z - 2, front - rng.randint(6, 9), rng.randint(7, 10), size=size)


BOSS_ARCHETYPES: dict[str, Callable[[Rng, float, int], tuple[Ship, Hull]]] = {
    "carrier": carrier,
    "dreadnought": dreadnought,
    "flying_wing": flying_wing,
    "twin_hull": twin_hull,
    "mothership": mothership,
    "gunline": gunline,
}


def finish(rng: Rng, ship: Ship, body: Hull, lopsided: bool) -> None:
    """Arm the core (a side cannon on a lopsided one, guns in its nose sometimes), then paint it like an enemy."""
    if lopsided:
        weapons.side_cannon(rng, ship, body)
    if not ship.weapons or rng.random() < 0.5:
        (weapons.nose_guns if rng.random() < 0.6 else weapons.gatling)(rng, ship, body)
    paint(rng, ship, body)
