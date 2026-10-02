"""Generate boss model candidates for the Boss candidates screen (src/pewpy/models/boss_candidates/).

    make boss-candidates                                  # 40 bosses, a new random batch each time
    make boss-candidates ARGS="--count 20 --seed 1234"    # the same batch again
    make boss-candidates ARGS="--append --count 10"       # add to the batch instead of replacing it

(or `uv run python -m pewpewdev.tools.make_boss_candidates ...`). Then open Main menu > Boss candidates in `make dev`.

Like the game's bosses, each candidate is a big core and destroyable parts placed on it. For candidate 007:
- `007.json`: the core's drawing (with its engines);
- `007_a.json`, `007_b.json`...: its parts' drawings;
- `007.parts.json`: where the parts go: {"parts": [{"drawing": "007_a", "x": ..., "y": ...}]}, in cubes from the
  core's middle (x right, y up the screen); a part used on both sides is listed twice.

Cores: 18 families (carrier, dreadnought, station, hammerhead, twin hull, flying wing, crescent, modular, citadel,
spider, trident, barge, mothership, chain, fortress, blade, gunline, ring cluster), a quarter of them combining two
(a second hull at the back or on the sides), with 0 to 3 appendages (big wings, arms ending in pods, armor spikes, a
halo ring, engine nacelles, radiator panels, masts); medium (41 to 61 cubes wide), large (up to 85) or huge (up to
115, half the screen); a fifth of them lopsided. Details: raised decks and a bridge, hangar bays, armor bands, engine
banks, lights, and a paint scheme (plain, two-tone or glowing seams). Parts (11 kinds: turrets, cannons, generators,
missile launchers, drills, missile pods, beam emitters, shield nodes, radar dishes, flak guns, claws), sized to the
boss, up to 10 on the biggest, each on a socket. Everything is a real 3D model ("layers"), sculpted from its plan
(src/pewpewdev/tools/shaping.py): a chamfered hull, higher on top than underneath, raised decks stacked on it with the bridge on
top, recessed panel lines and hangar bays, thin wings and sponsons; each part stands on the core's surface where it
is mounted, its barrels at half its height. As for the enemies (src/pewpewdev/tools/make_candidates.py), many more are
made than kept, and the ones kept are the most different from each other (outline, size, family, parts).
"""

import argparse
import json
import math
import random
import time
from collections.abc import Callable
from pathlib import Path

from pewpewdev.paths import GAME
from pewpewdev.tools.make_candidates import (
    ACCENTS,
    HULL_TINTS,
    LIVERIES,
    UNDERSIDE,
    Canvas,
    Rng,
    _bands,
    _markings,
    _panel_lines,
    _wing_edges,
    features,
    layered_drawing,
    most_different,
    trim,
)
from pewpewdev.tools.shaping import Shaping, engines_at_height, lifted, sculpt

DEFAULT_OUT = GAME / "models" / "boss_candidates"
LOPSIDED_SHARE = 0.2
COMBINED_SHARE = 0.25
SIZES = {  # (share, width range, height range), in cubes
    "medium": (0.35, (41, 61), (31, 51)),
    "large": (0.4, (61, 85), (41, 71)),
    "huge": (0.25, (85, 115), (55, 95)),
}
PARTS_BY_SIZE = {"medium": (0, 4), "large": (2, 7), "huge": (3, 10)}

# Thicker than the enemies (the game's bosses go up to 19 cubes).
CORE_GREYS = {  # char: (color, height in cubes)
    "N": ((0.26, 0.27, 0.29), 11),  # armor bands
    "h": ((0.37, 0.38, 0.41), 9),  # hull
    "H": ((0.5, 0.51, 0.54), 9),  # lighter hull bands
    "S": ((0.6, 0.61, 0.63), 15),  # superstructure
    "T": ((0.55, 0.56, 0.59), 13),  # superstructure, lower decks
    "k": ((0.17, 0.18, 0.2), 7),  # dark panel lines, hangar bays
    "r": ((0.13, 0.13, 0.15), 5),  # recesses
    "w": ((0.32, 0.33, 0.36), 3),  # wings, sponsons
    "W": ((0.45, 0.46, 0.49), 3),
    "o": ((0.08, 0.08, 0.09), 9),  # engine nozzles
    "x": ((0.22, 0.23, 0.25), 3),  # sockets under the parts (thin: the part stands out over them)
}
PART_GREYS = {
    "N": ((0.26, 0.27, 0.29), 9),
    "t": ((0.3, 0.31, 0.33), 9),  # housing
    "S": ((0.6, 0.61, 0.63), 13),  # dome, raised top
    "h": ((0.37, 0.38, 0.41), 7),
    "H": ((0.5, 0.51, 0.54), 7),
    "k": ((0.17, 0.18, 0.2), 5),
    "r": ((0.13, 0.13, 0.15), 5),  # barrels, tubes
    "W": ((0.45, 0.46, 0.49), 5),
}
BRIDGE = ((0.08, 0.2, 0.28), 15)


def core_shaping(cv: Canvas) -> Shaping:
    """How a core's plan becomes 3D: lower decks (T), the superstructure on them (S) with the bridge (c), its sensor
    (R) on top; thicker on bigger bosses.
    """
    top = max(3, min(7, round(cv.w * 0.06)))
    return Shaping(
        roles={
            "T": "raised",
            "S": "raised",
            "c": "raised",
            "R": "raised",
            "k": "seam",
            "g": "seam",
            "w": "wing",
            "W": "wing",
            "q": "wing",
            "r": "gun",
        },
        tiers={"T": 1, "S": 2, "c": 2, "R": 3},
        top=top,
        bottom=top - 1,
        edge=1,
        tier_height=2,
        wing=2,
        lift=0.04,
        fill="T",
    )


def part_shaping(cv: Canvas) -> Shaping:
    """How a part's plan becomes 3D: flat underneath (it stands on the core), its dome or glowing core raised, its
    barrels at half its height.
    """
    top = max(2, min(5, round(min(cv.w, cv.h) * 0.2)))
    return Shaping(
        roles={"S": "raised", "G": "raised", "k": "seam", "r": "gun"},
        tiers={"S": 1, "G": 1},
        top=top,
        bottom=1,
        tier_height=2,
        gun=top // 2,
        fill="t",
        plating="hHNt",
    )


# Core families: each draws a hull symmetric around column `mx`, from row `top` to row `bottom` (the back is at
# the top), `half` cubes to each side.

Family = Callable[[Rng, Canvas, float, float, float, float], None]


def carrier(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A long flat-topped hull with chamfered corners, a flight deck down the middle, sponsons on the sides."""
    cut, length = max(2.0, half * 0.25), bottom - top
    cv.polygon([(mx - half, top + cut), (mx - half + cut, top), (mx + half - cut, top), (mx + half, top + cut),
                (mx + half, bottom - 2 * cut), (mx, bottom), (mx - half, bottom - 2 * cut)], "h")  # fmt: skip
    cv.rect(mx - 2, mx + 2, top + 2, bottom - 2 * cut, "k")
    for y in range(round(top) + 4, round(bottom - 2 * cut), 4):
        cv.set(round(mx), y, "W")
    y = top + rng.uniform(0.15, 0.4) * length
    cv.rect(mx - half * 1.4, mx - half - 1, y, y + rng.uniform(0.25, 0.45) * length, "w", "both")


def dreadnought(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A huge arrowhead, stepped towards its middle."""
    length = bottom - top
    cv.polygon([(mx - half, top + rng.uniform(0.0, 0.25) * length), (mx, top), (mx + half, top + rng.uniform(0.0, 0.25) * length),
                (mx + 2, bottom), (mx - 2, bottom)], "h")  # fmt: skip
    for step, char in ((1, "T"), (2, "S")):
        inset = step * half / 3.5
        cv.polygon([(mx - half + inset, top + length * 0.2 + inset * 0.3), (mx, top + inset * 0.4),
                    (mx + half - inset, top + length * 0.2 + inset * 0.3), (mx, bottom - inset)], char)  # fmt: skip


def station(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """An octagonal ring around a hub, joined by spokes."""
    my, r = (top + bottom) / 2, min(half, (bottom - top) / 2)
    angles = [math.pi / 8 + i * math.pi / 4 for i in range(8)]
    cv.polygon([(mx + r * math.cos(a), my + r * math.sin(a)) for a in angles], "N")
    cv.polygon([(mx + (r - 4) * math.cos(a), my + (r - 4) * math.sin(a)) for a in angles], ".")
    cv.ellipse(mx, my, r * 0.35, r * 0.35, "h")
    spokes = rng.choice((2, 3, 4, 6))
    for i in range(spokes):
        a = math.pi / 2 + i * 2 * math.pi / spokes
        for dx in (0, 1):
            cv.line(mx + dx, my, mx + dx + r * math.cos(a), my + r * math.sin(a), "h")


def hammerhead(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A long body with a wide armored bar across its front."""
    body, head = half * rng.uniform(0.25, 0.4), (bottom - top) * rng.uniform(0.12, 0.2)
    cv.rect(mx - body, mx + body, top, bottom, "h")
    cv.rect(mx - half, mx + half, bottom - head - 2, bottom - 2, "N")
    cv.polygon([(mx - body, top + (bottom - top) * 0.2), (mx - half, top + (bottom - top) * 0.35),
                (mx - half, top + (bottom - top) * 0.45), (mx - body, top + (bottom - top) * 0.45)], "w", "both")  # fmt: skip


def twin_hull(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Two big hulls side by side, joined by bridges, a pod between them."""
    width, cut = half * rng.uniform(0.35, 0.5), max(2.0, half * 0.12)
    for left in (mx - half, mx + half - width):
        cv.polygon([(left, top + cut), (left + cut, top), (left + width - cut, top), (left + width, top + cut),
                    (left + width, bottom), (left, bottom)], "h")  # fmt: skip
    for _ in range(rng.randint(2, 4)):
        y = top + rng.uniform(0.15, 0.8) * (bottom - top)
        cv.rect(mx - half + width, mx + half - width, y, y + rng.randint(2, 4), "T")
    cv.ellipse(mx, (top + bottom) / 2, half * 0.2, (bottom - top) * 0.2, "h")


def flying_wing(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A huge delta with a blended body."""
    length = bottom - top
    back = top + rng.uniform(0.0, 0.2) * length
    cv.polygon([(mx - half, back + length * 0.2), (mx, top), (mx + half, back + length * 0.2), (mx + half, back + length * 0.35),
                (mx, bottom), (mx - half, back + length * 0.35)], "w")  # fmt: skip
    cv.ellipse(mx, top + length * 0.45, half * 0.28, length * 0.42, "h")


def crescent(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """An arc, its horns reaching forward."""
    length = bottom - top
    cv.ellipse(mx, top + length * 0.4, half, length * 0.4, "h")
    cv.ellipse(mx, top + length * 0.85, half * rng.uniform(0.5, 0.65), length * 0.5, ".")
    cv.ellipse(mx, top + length * 0.3, half * 0.25, length * 0.3, "T")


def modular(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Blocks of different sizes on a lattice of trusses."""
    cv.rect(mx - 1, mx + 1, top, bottom, "N")
    for y in range(round(top) + 2, round(bottom) - 3, rng.randint(6, 9)):
        cv.rect(mx - half + 2, mx, y, y + 1, "k", "both")
        for _ in range(rng.randint(1, 2)):
            width, height = rng.uniform(3, max(3.0, half / 2)), rng.randint(3, 6)
            left = mx - rng.uniform(width + 1, max(width + 1.5, half))
            cv.rect(left, left + width, y - height // 2, y + height // 2, "h", "both")
    cv.ellipse(mx, bottom - 5, 3, 4, "h")


def citadel(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Stacked tiers: a wide base at the front narrowing towards the back, like a fortress city."""
    tiers = rng.randint(3, 5)
    length = (bottom - top) / tiers
    for i in range(tiers):
        width = half * (0.35 + 0.65 * (i + 1) / tiers)
        cv.rect(mx - width, mx + width, top + i * length, top + (i + 1) * length - 1, "T" if i % 2 else "h")
        cv.rect(mx - width, mx - width + 1, top + i * length, top + (i + 1) * length - 1, "N", "both")


def spider(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A round body with legs reaching out, each ending in a claw."""
    my = (top + bottom) / 2
    body = min(half, (bottom - top) / 2) * rng.uniform(0.3, 0.45)
    legs = rng.randint(2, 4)
    for i in range(legs):
        a = math.radians(-60 + 120 * i / max(1, legs - 1))  # from forward-left to back-left
        end_x, end_y = mx - half * math.cos(a) * 0.95, my - (bottom - top) * 0.45 * math.sin(a)
        knee_x, knee_y = (mx + end_x) / 2, (my + end_y) / 2 - 3
        for a0, a1 in (((mx, my), (knee_x, knee_y)), ((knee_x, knee_y), (end_x, end_y))):
            for dx in (0, 1):
                cv.line(a0[0] + dx, a0[1], a1[0] + dx, a1[1], "N", "both")
        cv.ellipse(end_x, end_y, 2, 2, "h")
        cv.set(round(end_x), round(end_y) + 3, "r")
    cv.ellipse(mx, my, body, body * 1.2, "h")


def trident(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A heavy body at the back with three prongs reaching forward."""
    length = bottom - top
    split = top + length * rng.uniform(0.35, 0.5)
    cv.rect(mx - half, mx + half, top, split, "h")
    width = max(2.0, half * 0.14)
    for x in (mx - half + width, mx):
        cv.polygon([(x - width, split), (x + width, split), (x + 0.5, bottom - (0 if x == mx else length * 0.1)),
                    (x - 0.5, bottom - (0 if x == mx else length * 0.1))], "N", "both" if x != mx else "one")  # fmt: skip


def barge(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A long hull with rows of cargo containers and a small bridge tower at the back."""
    cv.rect(mx - half, mx + half, top + 3, bottom - 2, "h")
    cv.polygon([(mx - half, bottom - 2), (mx + half, bottom - 2), (mx, bottom)], "h")
    size = rng.randint(3, 5)
    for y in range(round(top) + 8, round(bottom) - 4, size + 1):
        for x in range(round(mx - half + 1), round(mx), size + 1):
            if rng.random() < 0.85:
                cv.rect(x, x + size - 1, y, y + size - 1, "T" if (x + y) % 2 else "S", "both")
    cv.rect(mx - 3, mx + 3, top, top + 6, "S")


def mothership(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A great disc with rings, a hangar mouth open at the front."""
    my = (top + bottom) / 2
    rx, ry = half, (bottom - top) / 2
    cv.ellipse(mx, my, rx, ry, "h")
    cv.ellipse(mx, my, rx * 0.8, ry * 0.8, "N")
    cv.ellipse(mx, my, rx * 0.76, ry * 0.76, "h")
    cv.ellipse(mx, my, rx * 0.35, ry * 0.35, "T")
    cv.rect(mx - rx * 0.15, mx + rx * 0.15, bottom - ry * 0.35, bottom, "k")  # the hangar mouth


def chain(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Segments linked in a column, like a train of hulls."""
    count = rng.randint(3, 5)
    length = (bottom - top) / count
    for i in range(count):
        middle = top + (i + 0.5) * length
        width = half * rng.uniform(0.5, 1.0)
        cv.ellipse(mx, middle, width, length * 0.42, "h" if i % 2 else "T")
    cv.rect(mx - 1, mx + 1, top, bottom, "N")


def fortress(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A square keep with round towers at its corners."""
    tower = max(3.0, half * 0.25)
    cv.rect(mx - half + tower, mx + half - tower, top + tower, bottom - tower, "h")
    for y in (top + tower, bottom - tower):
        cv.ellipse(mx - half + tower, y, tower, tower, "N")
        cv.ellipse(mx + half - tower, y, tower, tower, "N")
    cv.rect(mx - half + tower, mx + half - tower, top + tower + 3, top + tower + 4, "k")


def blade(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """A very long narrow wedge with fins along its sides."""
    width = half * rng.uniform(0.3, 0.45)
    cv.polygon([(mx - width, top), (mx + width, top), (mx, bottom)], "h")
    for i in range(rng.randint(2, 4)):
        y = top + (bottom - top) * (0.1 + 0.2 * i)
        cv.polygon([(mx - width * (1 - (y - top) / (bottom - top)), y), (mx - half, y + 2), (mx - half, y + 4),
                    (mx - width * (1 - (y + 5 - top) / (bottom - top)), y + 5)], "w", "both")  # fmt: skip


def gunline(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Several long tubes side by side, held by cross beams: a battery of guns."""
    tubes = rng.choice((3, 5))
    spacing = 2 * half / (tubes - 1)
    for i in range(tubes):
        x = mx - half + i * spacing
        cv.rect(x - 1.5, x + 1.5, top + (0 if i % 2 else 4), bottom - (0 if i == tubes // 2 else 4), "h")
    for y in (top + (bottom - top) * 0.3, top + (bottom - top) * 0.6):
        cv.rect(mx - half, mx + half, y, y + 2, "T")


def ring_cluster(rng: Rng, cv: Canvas, mx: float, top: float, bottom: float, half: float) -> None:
    """Rings joined together around a spine."""
    count = rng.randint(2, 3)
    length = (bottom - top) / count
    for i in range(count):
        middle = top + (i + 0.5) * length
        r = min(half, length / 2) * rng.uniform(0.7, 1.0)
        cv.ellipse(mx, middle, r, r, "N")
        cv.ellipse(mx, middle, r - 3, r - 3, ".")
    cv.rect(mx - 2, mx + 2, top, bottom, "h")


FAMILIES: dict[str, Family] = {
    "carrier": carrier,
    "dreadnought": dreadnought,
    "station": station,
    "hammerhead": hammerhead,
    "twin_hull": twin_hull,
    "flying_wing": flying_wing,
    "crescent": crescent,
    "modular": modular,
    "citadel": citadel,
    "spider": spider,
    "trident": trident,
    "barge": barge,
    "mothership": mothership,
    "chain": chain,
    "fortress": fortress,
    "blade": blade,
    "gunline": gunline,
    "ring_cluster": ring_cluster,
}


# Appendages, on the left (`side` "one") or both sides.


def big_wings(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    root, sweep = rng.uniform(0.3, 0.6) * cv.h, rng.uniform(-0.2, 0.3) * cv.h
    chord = rng.uniform(0.15, 0.3) * cv.h
    tip = max(2.0, chord * rng.uniform(0.2, 0.5))
    cv.polygon(
        [(mx - half * 0.5, root), (0, root - sweep), (0, root - sweep + tip), (mx - half * 0.5, root + chord)],
        "w",
        side,
    )


def arms(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    y = rng.uniform(0.3, 0.7) * cv.h
    end = rng.uniform(2, max(2.5, mx - half - 2))
    cv.rect(end, mx - half * 0.5, y, y + 2, "N", side)
    cv.ellipse(end, y + 1, 3, 4, "h")
    if side == "both":
        cv.ellipse(cv.mirror(end), y + 1, 3, 4, "h")


def spikes(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    for y in range(round(cv.h * 0.2), round(cv.h * 0.9), rng.randint(5, 8)):
        edge = next((x for x in range(cv.w) if cv.get(x, y) in "hHNT"), None)
        if edge is not None and edge > 3:
            cv.polygon([(edge + 0.5, y - 1), (edge - rng.uniform(3, 6), y + 1.5), (edge + 0.5, y + 2)], "N", side)


def halo(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    my = cv.h * rng.uniform(0.35, 0.6)
    r = min(cv.w / 2 - 1, cv.h / 2 - 1) * rng.uniform(0.8, 1.0)
    for a in range(0, 360, 2):
        x, y = mx + r * math.cos(math.radians(a)), my + r * 0.7 * math.sin(math.radians(a))
        cv.set(round(x), round(y), "N" if cv.get(round(x), round(y)) == "." else cv.get(round(x), round(y)))


def nacelles(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    x = rng.uniform(2, max(2.5, mx - half - 3))
    length = rng.uniform(0.3, 0.5) * cv.h
    cv.rect(x - 2, x + 2, 0, length, "h", side)
    cv.rect(x, mx - half * 0.5, length * 0.5, length * 0.5 + 2, "w", side)


def radiators(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    y, length = rng.uniform(0.1, 0.4) * cv.h, rng.randint(6, 14)
    left = rng.uniform(1, max(1.5, mx - half - 6))
    for i in range(length):
        cv.rect(left, mx - half * 0.6, y + i, y + i, "W" if i % 2 else "w", side)


def masts(rng: Rng, cv: Canvas, mx: float, half: float, side: str) -> None:
    for _ in range(rng.randint(1, 3)):
        cv.line(
            mx - half * rng.uniform(0.2, 0.6),
            rng.uniform(0.2, 0.6) * cv.h,
            rng.uniform(0, mx - half),
            rng.uniform(0, cv.h * 0.3),
            "r",
            side,
        )


APPENDAGES = [big_wings, arms, spikes, halo, nacelles, radiators, masts]


def core(rng: Rng, lopsided: bool) -> tuple[Canvas, str, str]:
    """The core's outline: (canvas, family, size class)."""
    size = rng.choices(list(SIZES), [share for share, _, _ in SIZES.values()])[0]
    _, widths, heights = SIZES[size]
    cv = Canvas(rng.randrange(widths[0], widths[1] + 1, 2), rng.randint(*heights))
    mx = cv.w // 2
    family = rng.choice(list(FAMILIES))
    reach = cv.w * rng.uniform(0.3, 0.45)  # half-width of the main hull (appendages go beyond)
    if rng.random() < COMBINED_SHARE:  # a second family: at the back, or on the sides
        second = rng.choice([name for name in FAMILIES if name != family])
        if rng.random() < 0.5:
            FAMILIES[family](rng, cv, mx, cv.h * 0.35, cv.h - 1, reach)
            FAMILIES[second](rng, cv, mx, 0, cv.h * 0.45, reach * 0.6)
        else:
            FAMILIES[family](rng, cv, mx, 0, cv.h - 1, reach * 0.6)
            side_x = mx - reach * 0.75
            FAMILIES[second](rng, cv, side_x, cv.h * 0.2, cv.h * 0.8, reach * 0.3)
            FAMILIES[second](rng, cv, cv.mirror(side_x), cv.h * 0.2, cv.h * 0.8, reach * 0.3)
        family = f"{family}+{second}"
    else:
        FAMILIES[family](rng, cv, mx, 0, cv.h - 1, reach)
    for _ in range(rng.choice((0, 1, 1, 2, 3))):
        side = "one" if lopsided and rng.random() < 0.6 else "both"
        rng.choice(APPENDAGES)(rng, cv, mx, reach, side)
    if lopsided:  # a chunk shorn off one side, a bulge on the other
        cut = rng.uniform(0.2, 0.35) * cv.w
        cv.polygon([(-0.5, rng.uniform(0.2, 0.6) * cv.h), (cut, -0.5), (-0.5, -0.5)], ".")
        y = rng.uniform(0.3, 0.7) * cv.h
        cv.rect(cv.w - rng.randint(4, 8), cv.w - 1, y, y + rng.randint(4, 8), "N")
    return cv, family, size


# Details.


def superstructure(rng: Rng, cv: Canvas) -> None:
    """Raised decks towards the back, a bridge with a sensor near the middle, hangar bays, lights."""
    mx = _middle(cv)
    top = rng.randint(2, max(2, cv.h // 3))
    width = rng.randint(2, max(2, cv.w // 10))
    for x, y in cv.cells_of("hH"):
        if abs(x - mx) <= width and top <= y <= top + cv.h // 4:
            cv.set(x, y, "T")
    for x, y in cv.cells_of("T"):
        if abs(x - mx) <= max(1, width // 2) and y <= top + cv.h // 6:
            cv.set(x, y, "S")
    bridge = top + cv.h // 6
    for x in range(mx - 1, mx + 2):
        cv.set(x, bridge, "c")
    cv.set(mx, bridge, "R")
    _hangars(rng, cv)
    _lights(rng, cv)


def _hangars(rng: Rng, cv: Canvas) -> None:
    """Hangar bays: dark rectangles on the hull."""
    for _ in range(rng.randint(1, 3 + cv.w // 30)):
        x, y = rng.randrange(cv.w), rng.randrange(cv.h)
        if cv.get(x, y) in "hH":
            cv.rect(x - 1, x + 1, y, y + rng.randint(2, 4), "k", "both" if rng.random() < 0.7 else "one")


def _lights(rng: Rng, cv: Canvas) -> None:
    """Rows of lights along the armor."""
    rows = set(range(3, cv.h, rng.randint(5, 8)))
    for x, y in cv.cells_of("N"):
        if y in rows and x % 3 == 0:
            cv.set(x, y, "p")


def _middle(cv: Canvas) -> int:
    counts = [sum(cv.filled(x, y) for y in range(cv.h)) for x in range(cv.w)]
    return max(range(cv.w), key=lambda x: (counts[x], -abs(x - cv.w // 2)))


def armor(rng: Rng, cv: Canvas) -> None:
    """Armor bands along the hull's edges."""
    for x, y in cv.cells_of("hH"):
        if any(not cv.filled(x + dx, y + dy) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))) and rng.random() < 0.8:
            cv.set(x, y, "N")


def paint(rng: Rng, cv: Canvas) -> str:
    """A paint scheme: plain, two-tone (big areas of the hull in the livery color) or glowing seams."""
    scheme = rng.choice(("plain", "plain", "two-tone", "seams"))
    if scheme == "two-tone":
        split = rng.uniform(0.3, 0.7) * cv.h
        stripes = rng.random() < 0.5
        for x, y in cv.cells_of("hH"):
            if (stripes and (y // 4) % 3 == 0) or (not stripes and y < split):
                cv.set(x, y, "L")
    elif scheme == "seams":
        for x, y in cv.cells_of("k"):
            if rng.random() < 0.5:
                cv.set(x, y, "g")
    return scheme


def engine_bank(rng: Rng, cv: Canvas) -> list[dict]:
    """Nozzles along the back of the hull, spread out, with big flames (more on bigger bosses)."""
    backs = []
    for x in range(cv.w):
        top = next((y for y in range(cv.h) if cv.filled(x, y)), None)
        if top is not None and cv.get(x, top) in "hHNTSkL" and top <= cv.h // 3:
            backs.append((top, x))
    chosen: list[tuple[int, int]] = []
    wanted = rng.randint(3, 6 + cv.w // 20)
    for top, x in sorted(backs):
        if len(chosen) < wanted and all(abs(x - other) >= 4 for _, other in chosen):
            chosen.append((top, x))
    width, length = rng.uniform(3.5, 6.0) * (1 + cv.w / 150), rng.randint(10, 16 + cv.w // 10)
    for top, x in chosen:
        cv.rect(x - 1, x + 1, top, top, "o")
    return [{"x": x, "y": top, "width": round(width, 1), "length": length, "towards": "top"} for top, x in chosen]


# Parts: drawn on their own small canvas, pointing down like the rest.


def part_turret(rng: Rng, cv: Canvas) -> None:
    mx, my = cv.w // 2, cv.h * 0.45
    r = min(cv.w, cv.h) * 0.35
    cv.ellipse(mx, my, r + 1, r + 1, "N")
    cv.ellipse(mx, my, r, r, "t")
    cv.ellipse(mx, my, r * 0.5, r * 0.5, "S")
    barrels = rng.choice((1, 2, 3))
    for i in range(barrels):
        x = mx + (i - (barrels - 1) / 2) * 2
        cv.line(x, my, x, cv.h - 1, "r")


def part_cannon(rng: Rng, cv: Canvas) -> None:
    mx = cv.w // 2
    cv.rect(mx - cv.w // 3, mx + cv.w // 3, 0, cv.h * 0.55, "t")
    cv.rect(mx - 1, mx + 1, cv.h * 0.55, cv.h - 1, "r")
    cv.rect(mx - 2, mx + 2, cv.h - 3, cv.h - 1, "N")  # the muzzle
    cv.rect(mx - cv.w // 3, mx + cv.w // 3, 1, 2, "k")


def part_generator(rng: Rng, cv: Canvas) -> None:
    mx, my = cv.w // 2, cv.h / 2
    r = min(cv.w, cv.h) / 2 - 1
    for angle in range(0, 360, 90 if rng.random() < 0.5 else 60):  # fins
        a = math.radians(angle)
        cv.line(mx, my, mx + (r + 1) * math.cos(a), my + (r + 1) * math.sin(a), "W")
    cv.ellipse(mx, my, r * 0.7, r * 0.7, "t")
    cv.ellipse(mx, my, r * 0.35, r * 0.35, "G")  # the glowing core


def part_launcher(rng: Rng, cv: Canvas) -> None:
    cv.rect(1, cv.w - 2, 1, cv.h - 2, "t")
    for y in range(2, cv.h - 2, 3):
        for x in range(2, cv.w - 2, 3):
            cv.set(x, y, "r")  # a tube
    cv.rect(1, cv.w - 2, cv.h - 2, cv.h - 2, "N")


def part_drill(rng: Rng, cv: Canvas) -> None:
    mx = cv.w // 2
    cv.rect(mx - cv.w // 3, mx + cv.w // 3, 0, cv.h * 0.3, "t")
    cv.polygon([(mx - cv.w / 2.6, cv.h * 0.3), (mx + cv.w / 2.6, cv.h * 0.3), (mx, cv.h - 0.5)], "h")
    rows = set(range(round(cv.h * 0.35), cv.h, 2))  # the thread
    for x, y in cv.cells_of("h"):
        if y in rows:
            cv.set(x, y, "W")


def part_missile_pod(rng: Rng, cv: Canvas) -> None:
    """A cluster of missile tubes, their warheads showing."""
    mx, my = cv.w / 2 - 0.5, cv.h / 2 - 0.5
    cv.ellipse(mx, my, cv.w / 2 - 0.5, cv.h / 2 - 0.5, "N")
    for y in range(2, cv.h - 1, 3):
        for x in range(2, cv.w - 1, 3):
            if cv.get(x, y) == "N":
                cv.set(x, y, "G")


def part_emitter(rng: Rng, cv: Canvas) -> None:
    """A beam emitter: a long prism with a glowing tip."""
    mx = cv.w // 2
    cv.polygon([(mx - cv.w * 0.4, 0), (mx + cv.w * 0.4, 0), (mx + 1.5, cv.h - 3), (mx - 1.5, cv.h - 3)], "t")
    cv.rect(mx - 1, mx + 1, cv.h - 3, cv.h - 1, "G")
    cv.rect(mx, mx, 1, cv.h - 4, "S")


def part_shield_node(rng: Rng, cv: Canvas) -> None:
    """A hexagonal shield projector, glowing in the middle."""
    mx, my, r = cv.w / 2 - 0.5, cv.h / 2 - 0.5, min(cv.w, cv.h) / 2 - 0.5
    hexagon = [
        (mx + r * math.cos(math.radians(30 + 60 * i)), my + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)
    ]
    cv.polygon(hexagon, "N")
    cv.polygon([(mx + (x - mx) * 0.7, my + (y - my) * 0.7) for x, y in hexagon], "t")
    cv.ellipse(mx, my, r * 0.3, r * 0.3, "G")


def part_radar(rng: Rng, cv: Canvas) -> None:
    """A dish on a mast."""
    mx = cv.w / 2 - 0.5
    cv.rect(mx - 1, mx + 1, cv.h * 0.4, cv.h - 1, "t")
    cv.ellipse(mx, cv.h * 0.35, cv.w / 2 - 0.5, cv.h * 0.3, "W")
    cv.ellipse(mx, cv.h * 0.35, 1.2, 1.2, "S")


def part_flak(rng: Rng, cv: Canvas) -> None:
    """A square mount with four short barrels."""
    cv.rect(1, cv.w - 2, 1, cv.h * 0.6, "t")
    for x in (cv.w * 0.25, cv.w * 0.42, cv.w * 0.58, cv.w * 0.75):
        cv.line(x, cv.h * 0.6, x, cv.h - 1, "r")


def part_claw(rng: Rng, cv: Canvas) -> None:
    """A heavy claw: a base and two curved pincers."""
    mx = cv.w // 2
    cv.rect(mx - cv.w * 0.3, mx + cv.w * 0.3, 0, cv.h * 0.35, "t")
    for side in (-1, 1):
        cv.polygon([(mx + side * 1, cv.h * 0.35), (mx + side * cv.w * 0.45, cv.h * 0.35), (mx + side * cv.w * 0.25, cv.h - 0.5),
                    (mx + side * 0.5, cv.h * 0.6)], "N")  # fmt: skip


PARTS: dict[str, Callable[[Rng, Canvas], None]] = {
    "turret": part_turret,
    "cannon": part_cannon,
    "generator": part_generator,
    "launcher": part_launcher,
    "drill": part_drill,
    "missile_pod": part_missile_pod,
    "emitter": part_emitter,
    "shield_node": part_shield_node,
    "radar": part_radar,
    "flak": part_flak,
    "claw": part_claw,
}


def part(rng: Rng, kind: str, boss_width: int) -> Canvas:
    """A part, sized to its boss."""
    scale = boss_width / 60
    size = max(9, round(rng.uniform(11, 23) * scale)) | 1  # odd
    cv = Canvas(size, max(9, round(size * rng.uniform(0.8, 1.4))))
    PARTS[kind](rng, cv)
    trim(cv, True)
    return cv


def mount(rng: Rng, cv: Canvas, symmetric: bool, size: str) -> list[tuple[str, int, int, bool]]:
    """Where the parts go: (kind, x, y, mirrored too) on hull cells of the core, in cubes from its top-left."""
    low, high = PARTS_BY_SIZE[size]
    wanted = rng.randint(low, high)
    kinds = rng.sample(list(PARTS), rng.randint(1, 3))  # a boss uses a few kinds of parts, not all of them
    spots = [(x, y) for x, y in cv.cells_of("hHNTwL") if x < cv.w // 2 - 3]
    spacing = max(8, cv.w // 8)
    mounts: list[tuple[str, int, int, bool]] = []
    placed = 0
    while placed < wanted and spots:
        x, y = rng.choice(spots)
        mirrored = symmetric or rng.random() < 0.5
        mounts.append((rng.choice(kinds), x, y, mirrored))
        placed += 2 if mirrored else 1
        spots = [(sx, sy) for sx, sy in spots if abs(sx - x) > spacing or abs(sy - y) > spacing]
    if rng.random() < 0.35:  # something in the middle
        mounts.append((rng.choice(kinds), cv.w // 2, rng.randint(cv.h // 3, cv.h * 2 // 3), False))
    return mounts


def socket(cv: Canvas, x: int, y: int, part_cv: Canvas, mirrored: bool) -> None:
    """A thin plate on the core under the part (so the part stands out over it, rather than clashing)."""
    half_w, half_h = part_cv.w // 2 - 1, part_cv.h // 2 - 1
    for sx in [x] + ([cv.w - 1 - x] if mirrored else []):
        for cy in range(y - half_h, y + half_h + 1):
            for cx in range(sx - half_w, sx + half_w + 1):
                if cv.filled(cx, cy):
                    cv.set(cx, cy, "x")


def palette(greys: dict, tint: tuple[float, float, float], accent: str, livery: tuple) -> dict:
    marking, sensor = ACCENTS[accent]
    entries: dict[str, tuple[tuple[float, ...], int]] = {
        char: (tuple(round(min(1.0, c * t), 3) for c, t in zip(color, tint, strict=True)), height)
        for char, (color, height) in greys.items()
    }
    entries["c"] = BRIDGE
    entries["p"] = (marking, 11)
    entries["q"] = (marking, 3)  # markings on wings: as thin as them
    entries["g"] = (sensor, 7)  # glowing seams
    entries["G"] = (sensor, 11)  # a part's glowing core
    entries["R"] = (sensor, 17)
    entries["L"] = (livery, 9)
    entries["D"] = (tuple(round(c * UNDERSIDE, 3) for c in entries["h"][0]), 1)  # the underside
    return {char: {"color": list(color), "height": height} for char, (color, height) in entries.items()}


def boss(rng: Rng, lopsided: bool) -> tuple[list[float], Callable[[], dict]] | None:
    """A boss: its features (for telling bosses apart), and what makes its drawings {"core": ..., "parts": [(drawing,
    x, y)]} (only the bosses kept are built in 3D).
    """
    cv, family, size = core(rng, lopsided)
    trim(cv, not lopsided)
    if cv.w < 20 or cv.h < 15:
        return None
    _bands(rng, cv)
    _wing_edges(cv)
    _panel_lines(rng, cv)
    armor(rng, cv)
    superstructure(rng, cv)
    scheme = paint(rng, cv)
    _markings(rng, cv)
    parts = []
    for part_kind, x, y, mirrored in mount(rng, cv, not lopsided, size):
        part_cv = part(rng, part_kind, cv.w)
        socket(cv, x, y, part_cv, mirrored)
        parts.append((part_cv, x, y, mirrored))
    engines = engine_bank(rng, cv)
    if not lopsided:
        for row in cv.cells:
            for x in range(cv.w // 2):
                row[cv.w - 1 - x] = row[x]
        engines = [{**engine, "x": x} for engine in engines for x in {engine["x"], cv.w - 1 - engine["x"]}]
    tint = HULL_TINTS[rng.choice(list(HULL_TINTS))]
    accent, livery = rng.choice(list(ACCENTS)), rng.choice(LIVERIES)
    # From the core's middle, in cubes, y up the screen.
    spots = [(part_cv, px, y) for part_cv, x, y, mirrored in parts for px in [x] + ([cv.w - 1 - x] if mirrored else [])]
    placed = [(part_cv, px - (cv.w - 1) / 2, (cv.h - 1) / 2 - y) for part_cv, px, y in spots]

    def make() -> dict:
        cells, heights = sculpt(cv, core_shaping(cv))
        core_drawing = {
            **layered_drawing(cells, cv, palette(CORE_GREYS, tint, accent, livery)),
            "engines": engines_at_height(engines, heights),
        }
        colors = palette(PART_GREYS, tint, accent, livery)
        shaped = {id(part_cv): sculpt(part_cv, part_shaping(part_cv))[0] for part_cv, _, _ in spots}
        drawings = []
        for (part_cv, px, y), (_, x, up) in zip(spots, placed, strict=True):
            # Standing on the core's top there: its lowest cubes just above the core's highest (no overlap).
            lift = heights.get((px, y), (0, 0))[1] + 1 + part_shaping(part_cv).bottom
            drawings.append((layered_drawing(lifted(shaped[id(part_cv)], lift), part_cv, colors), x, up))
        return {"core": core_drawing, "parts": drawings}

    return _features(cv, family, scheme, placed, not lopsided), make


def _features(cv: Canvas, family: str, scheme: str, parts: list, symmetric: bool) -> list[float]:
    """For telling bosses apart: the outline and size (like the enemies), the family, the paint, the parts."""
    families = [0.8 * (name in family.split("+")) for name in FAMILIES]
    spread = max((math.hypot(x, y) for _, x, y in parts), default=0.0) / max(cv.w, 1)
    return [
        *features(cv.rows(), symmetric),
        *families,
        0.5 * (scheme != "plain"),
        len(parts) / 6,
        2 * spread,
        3 * cv.w / 115,  # bigger ones stand apart more than the enemies' feature does at this size
    ]


def generate(count: int, seed: int, pool_factor: int) -> list[dict]:
    rng = random.Random(seed)  # noqa: S311 - drawings, not cryptography
    lopsided = round(count * LOPSIDED_SHARE)
    kept = []
    for group, wanted in ((False, count - lopsided), (True, lopsided)):
        pool = [made for _ in range(wanted * pool_factor) if (made := boss(rng, group)) is not None]
        if pool and wanted:
            kept += [make() for make in most_different(pool, wanted)]
    rng.shuffle(kept)
    return kept


def write(out: Path, number: int, candidate: dict) -> None:
    name = f"{number:03d}"
    (out / f"{name}.json").write_text(json.dumps(candidate["core"], indent=2) + "\n")
    drawings: dict[str, str] = {}  # the same part drawing placed twice is written once
    layout = []
    for part_drawing, x, y in candidate["parts"]:
        text = json.dumps(part_drawing, indent=2) + "\n"
        if text not in drawings:
            drawings[text] = f"{name}_{chr(ord('a') + len(drawings))}"
            (out / f"{drawings[text]}.json").write_text(text)
        layout.append({"drawing": drawings[text], "x": round(x, 2), "y": round(y, 2)})
    (out / f"{name}.parts.json").write_text(json.dumps({"parts": layout}, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=200, help="how many bosses to write (default 40)")
    parser.add_argument("--seed", type=int, help="the same seed makes the same batch (default: a new one)")
    parser.add_argument("--pool", type=int, default=6, help="how many generated for each one kept (default 6)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="where (default: the game's boss candidates)")
    parser.add_argument("--append", action="store_true", help="number after the ones there instead of replacing them")
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else int(time.time() * 1000) % 1_000_000
    args.out.mkdir(parents=True, exist_ok=True)
    existing = sorted(args.out.glob("*.json"))
    first = 1
    if args.append:
        first = max((int(path.name.split(".")[0].split("_")[0]) for path in existing), default=0) + 1
    else:
        for path in existing:
            path.unlink()
    for number, candidate in enumerate(generate(args.count, seed, args.pool), start=first):
        write(args.out, number, candidate)
    print(f"wrote {args.count} boss candidates ({first:03d} to {first + args.count - 1:03d}) to {args.out}")
    print(f"seed {seed}: --seed {seed} makes the same batch again")


if __name__ == "__main__":
    main()
