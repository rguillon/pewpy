"""Generate enemy model candidates: voxel drawings for the Candidates screen (src/pewpy/models/candidates/).

    uv run python -m tools.make_candidates                     # 200 ships, a new random batch each time
    uv run python -m tools.make_candidates --kind aircraft --count 50
    uv run python -m tools.make_candidates --seed 1234           # the same batch again
    uv run python -m tools.make_candidates --append --count 20   # add to the batch instead of replacing it

(or `make candidates ARGS="--kind aircraft --count 50"`). Then open Main menu > Enemy candidates (or "Reload models" there).

Enemies point down the screen: nose on the last row, engines at the back (flames "towards": "top"). Kinds:
- aircraft: a slender fuselage with an ogive nose, thin wings tapering to their tips (swept, delta, cranked,
  forward-swept, ogival or long and straight), a tailplane or canards, thin fins, slim engines;
- industrial: a core hull (spindle, block, wedge, egg, segmented, cross, crescent, frame, diamond, arrowhead) with
  1 to 3 attachments (wings, nacelles, booms, mandibles, fins, turrets, a side cannon, containers, radiators,
  antennas), symmetric or lopsided.
Every ship is a real 3D model ("layers"): the aircraft are built from their parts (`aircraft_layers`); the industrial
ships are drawn as a plan, then sculpted (tools/shaping.py): a hull chamfered from its outline, higher on top than
underneath, a spine and a cockpit raised on it, recessed panel lines, thin wings rising to their tips, rounded pods.
Many more ships are generated than kept (`--pool`): the ones kept are the most different from each other (outline,
size, proportions), so there are no near-duplicates.
"""

import argparse
import json
import math
import random
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from tools.shaping import Shaping, engines_at_height, sculpt

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "src" / "pewpy" / "models" / "candidates"
# Shares of each group, by --kind.
MIXES = {
    "all": {"aircraft": 0.45, "symmetric": 0.32, "lopsided": 0.23},
    "aircraft": {"aircraft": 1.0},
    "industrial": {"symmetric": 0.6, "lopsided": 0.4},
}

HULL_TINTS = {
    "grey": (1.0, 1.0, 1.0),
    "warm": (1.08, 1.0, 0.9),
    "blue": (0.9, 0.97, 1.1),
    "olive": (0.95, 1.0, 0.78),
    "dark": (0.68, 0.68, 0.74),
    "sand": (1.15, 1.05, 0.85),
    "rust": (1.1, 0.85, 0.72),
    "white": (1.35, 1.35, 1.35),
}
ACCENTS = {  # (markings, sensor)
    "red": ((0.8, 0.16, 0.12), (1.0, 0.2, 0.1)),
    "orange": ((0.9, 0.45, 0.1), (1.0, 0.6, 0.15)),
    "yellow": ((0.8, 0.65, 0.12), (1.0, 0.85, 0.2)),
    "green": ((0.2, 0.65, 0.25), (0.35, 1.0, 0.4)),
    "cyan": ((0.12, 0.6, 0.72), (0.3, 0.95, 1.0)),
    "purple": ((0.5, 0.2, 0.72), (0.75, 0.35, 1.0)),
    "magenta": ((0.78, 0.18, 0.55), (1.0, 0.3, 0.75)),
}
LIVERIES = [
    (0.55, 0.12, 0.1),
    (0.15, 0.25, 0.5),
    (0.5, 0.42, 0.12),
    (0.2, 0.35, 0.2),
    (0.3, 0.3, 0.33),
    (0.45, 0.2, 0.45),
]
GREYS = {  # char: (color, height in cubes)
    "N": ((0.26, 0.27, 0.29), 5),  # heavy plates
    "h": ((0.37, 0.38, 0.41), 3),  # hull
    "H": ((0.5, 0.51, 0.54), 3),  # lighter hull bands
    "S": ((0.6, 0.61, 0.63), 5),  # spine, fins, raised parts
    "k": ((0.17, 0.18, 0.2), 1),  # dark panel lines, flaps
    "r": ((0.13, 0.13, 0.15), 3),  # gun barrels
    "w": ((0.32, 0.33, 0.36), 1),  # wings
    "W": ((0.45, 0.46, 0.49), 1),  # lighter wing panels, leading edges
    "o": ((0.08, 0.08, 0.09), 3),  # engine nozzles
    "t": ((0.3, 0.31, 0.33), 5),  # turrets, containers
}
COCKPIT = ((0.08, 0.2, 0.28), 5)
UNDERSIDE = 0.72  # the hull's underside, this much as bright as its plating
HULL = "hHNSkt"  # what counts as hull (for engines)

Point = tuple[float, float]
Rng = random.Random
T = TypeVar("T")


class Canvas:
    """A drawing being made: rows of characters, "." for nothing. Row 0 is the back (top of the screen)."""

    def __init__(self, width: int, height: int) -> None:
        self.w, self.h = width, height
        self.cells = [["."] * width for _ in range(height)]

    def set(self, x: int, y: int, char: str) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.cells[y][x] = char

    def get(self, x: int, y: int) -> str:
        return self.cells[y][x] if 0 <= x < self.w and 0 <= y < self.h else "."

    def filled(self, x: int, y: int) -> bool:
        return self.get(x, y) != "."

    def mirror(self, x: float) -> float:
        return self.w - 1 - x

    def polygon(self, points: list[Point], char: str, side: str = "one") -> None:
        """Fill a polygon (the cells whose middle is inside); side "both" also fills its mirror image."""
        shapes = [points] + ([[(self.mirror(x), y) for x, y in points]] if side == "both" else [])
        for shape in shapes:
            xs, ys = [x for x, _ in shape], [y for _, y in shape]
            for y in self._span(min(ys), max(ys), self.h):  # only the cells in its bounding box
                for x in self._span(min(xs), max(xs), self.w):
                    if _inside(x, y, shape):
                        self.set(x, y, char)

    @staticmethod
    def _span(low: float, high: float, size: int) -> range:
        return range(max(0, math.floor(low)), min(size, math.ceil(high) + 1))

    def rect(self, x0: float, x1: float, y0: float, y1: float, char: str, side: str = "one") -> None:
        corners = [(x0 - 0.5, y0 - 0.5), (x1 + 0.5, y0 - 0.5), (x1 + 0.5, y1 + 0.5), (x0 - 0.5, y1 + 0.5)]
        self.polygon(corners, char, side)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, char: str) -> None:
        for y in self._span(cy - ry, cy + ry, self.h):
            for x in self._span(cx - rx, cx + rx, self.w):
                if ((x - cx) / max(rx, 0.1)) ** 2 + ((y - cy) / max(ry, 0.1)) ** 2 <= 1.0:
                    self.set(x, y, char)

    def line(self, x0: float, y0: float, x1: float, y1: float, char: str, side: str = "one") -> None:
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(steps + 1):
            t = i / steps
            x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
            self.set(x, y, char)
            if side == "both":
                self.set(round(self.mirror(x)), y, char)

    def rows_chars(self) -> str:
        """Every character drawn."""
        return "".join({char for row in self.cells for char in row} - {"."})

    def cells_of(self, chars: str) -> list[tuple[int, int]]:
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.get(x, y) in chars]

    def rows(self) -> list[str]:
        return ["".join(row) for row in self.cells]


def _inside(x: float, y: float, points: list[Point]) -> bool:
    inside = False
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1], strict=True):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


# Aircraft.


class Parts(Canvas):
    """What each cell of an aircraft's drawing is, for building it in 3D (see `aircraft_layers`): "F" fuselage,
    "W" wing or tailplane, "V" upright fin, "P" engine pod, "G" gun.
    """


def aircraft(rng: Rng) -> tuple[Canvas, bool, Parts]:
    small = rng.random() < 0.25
    width = rng.randrange(9, 16, 2) if small else rng.randrange(15, 32, 2)
    height = rng.randint(9, 15) if small else rng.randint(14, 30)
    cv, parts = Canvas(width, height), Parts(width, height)
    body = rng.choice((0.6, 1.0)) if small else rng.choice((0.6, 1.0, 1.0, 1.5, 2.0))
    _fuselage(rng, cv, body)
    root_x = width // 2 - round(body) - 0.5
    plan = rng.choice(("swept", "swept", "delta", "cranked", "forward", "ogival", "straight"))
    front = height * rng.uniform(0.5, 0.72)  # the wing root's leading edge (towards the nose)
    points = WING_PLANS[plan](rng, height, root_x, front)
    cv.polygon(points, "w", "both")
    parts.polygon(points, "W", "both")
    if plan not in ("delta", "ogival") or rng.random() < 0.3:
        _tail(rng, cv, root_x, front, min(y for _, y in points))
    for x, y in cv.cells_of("w"):
        parts.set(x, y, "W")  # the tailplane too
    for x, y in cv.cells_of("h"):
        parts.set(x, y, "F")  # the fuselage, over the wings' roots
    _fins(rng, cv, body)
    for x, y in cv.cells_of("S"):
        parts.set(x, y, "V")
    _pods_and_weapons(rng, cv, root_x, front)
    for x, y in cv.cells_of("N"):
        parts.set(x, y, "P")
    for x, y in cv.cells_of("r"):
        parts.set(x, y, "G")
    if rng.random() < 0.12:  # the odd lopsided one: a pod on one wing only
        x = round(root_x * 0.4)
        cv.rect(x, x + 1, front - 4, front, "t")
        parts.rect(x, x + 1, front - 4, front, "P")
        return cv, False, parts
    return cv, True, parts


AIRCRAFT_DIHEDRAL = 0.06  # wings rise towards their tips: cubes up per cube out
AIRCRAFT_FIN = 2  # an upright fin stands this many cubes above the fuselage at its front, more towards the back


def aircraft_layers(cv: Canvas, parts: Parts) -> dict[tuple[int, int, int], str]:
    """The aircraft in 3D: (column, row, layer) -> its drawing's character; layers from the middle plane, negative
    ones up towards the camera. A round fuselage (its width on the drawing gives its depth), a canopy on top of it,
    thin wings and tailplanes rising a little towards their tips, upright fins, pods and guns slung underneath.
    """
    middle = (cv.w - 1) / 2
    cells: dict[tuple[int, int, int], str] = {}
    fin_rows = sorted({y for _, y in parts.cells_of("V")})
    for x, y in cv.cells_of(cv.rows_chars()):
        char, part = cv.get(x, y), parts.get(x, y)
        if part == "F":
            radius = sum(parts.get(column, y) == "F" for column in range(cv.w)) / 2 + 0.3
            depth = round(math.sqrt(max(0.0, radius * radius - (x - middle) ** 2)))
            top = depth + (1 if char in "cR" else 0)  # the canopy bulges on top
            layers = range(-top, depth + 1)
        elif part == "V":
            height = AIRCRAFT_FIN + (fin_rows[-1] - y if fin_rows else 0)  # taller towards the back
            layers = range(-height, 1)
        elif part == "P":
            layers = range(2)  # under the wing
        elif part == "G":
            layers = range(1, 2)
        else:  # wings, tailplanes, and anything else thin
            layers = range(-round(abs(x - middle) * AIRCRAFT_DIHEDRAL), -round(abs(x - middle) * AIRCRAFT_DIHEDRAL) + 1)
        for layer in layers:
            cells[x, y, layer] = char
    return cells


def layered_drawing(cells: dict[tuple[int, int, int], str], cv: Canvas, colors: dict) -> dict:
    """A 3D drawing: its layers from the top (nearest the camera) down, symmetric around the middle plane (the
    game puts the middle one on it), and each character's color.
    """
    extent = max(abs(layer) for _, _, layer in cells)
    layers = [
        ["".join(cells.get((x, y, layer), ".") for x in range(cv.w)) for y in range(cv.h)]
        for layer in range(-extent, extent + 1)
    ]
    used = set(cells.values())
    return {
        "layers": layers,
        "palette": {char: {"color": entry["color"]} for char, entry in colors.items() if char in used},
    }


def _fuselage(rng: Rng, cv: Canvas, body: float) -> None:
    """A thin tail at the back, full width in the middle, an ogive nose."""
    middle = cv.w // 2
    nose = max(2, round(cv.h * rng.uniform(0.2, 0.35)))
    for y in range(cv.h):
        half = body
        if y >= cv.h - nose:
            t = (y - (cv.h - nose) + 1) / (nose + 1)
            half = body * math.sqrt(max(0.0, 1 - t * t))
        elif y < 2:
            half = max(0.6, body * 0.7)
        for x in range(round(middle - half), round(middle + half) + 1):
            cv.set(x, y, "h")


def _delta(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
    back = front - height * rng.uniform(0.5, 0.7)
    return [(root_x, front), (-0.5, back + 1.2), (-0.5, back), (root_x, back)]


def _ogival(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
    """A delta whose leading edge curves out from the nose to the tip."""
    back = front - height * rng.uniform(0.5, 0.7)
    points = [(root_x, front + 1)]
    for i in range(1, 8):
        t = i / 7
        points.append((root_x - (root_x + 0.5) * t**0.6, front + 1 - (front - back - 1) * t**1.8))
    return [*points, (-0.5, back), (root_x, back)]


def _cranked(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
    chord = height * rng.uniform(0.35, 0.5)
    crank_x = root_x - (root_x + 0.5) * rng.uniform(0.35, 0.5)
    crank_y = front - chord * 0.55
    tip_y = crank_y - (crank_x + 0.5) * rng.uniform(0.15, 0.45)
    return [
        (root_x, front),
        (crank_x, crank_y),
        (-0.5, tip_y),
        (-0.5, tip_y - max(1.0, chord * 0.12)),
        (root_x, front - chord),
    ]


def _tapered(
    sweep_range: tuple[float, float], chord_range: tuple[float, float]
) -> Callable[[Rng, int, float, float], list[Point]]:
    """A wing tapering to its tip, swept back (positive) or forward (negative)."""

    def plan(rng: Rng, height: int, root_x: float, front: float) -> list[Point]:
        chord = height * rng.uniform(*chord_range)
        tip_chord = max(1.0, chord * rng.uniform(0.25, 0.5))
        tip_front = front - (root_x + 0.5) * rng.uniform(*sweep_range)
        return [(root_x, front), (-0.5, tip_front), (-0.5, tip_front - tip_chord), (root_x, front - chord)]

    return plan


WING_PLANS: dict[str, Callable[[Rng, int, float, float], list[Point]]] = {
    "swept": _tapered((0.4, 1.0), (0.22, 0.35)),
    "forward": _tapered((-0.6, -0.3), (0.22, 0.35)),
    "straight": _tapered((0.0, 0.15), (0.12, 0.2)),
    "delta": _delta,
    "ogival": _ogival,
    "cranked": _cranked,
}


def _tail(rng: Rng, cv: Canvas, root_x: float, front: float, wing_back: float) -> None:
    """A small swept tailplane at the back, or canards near the nose."""
    span = (root_x + 0.5) * rng.uniform(0.3, 0.5)
    if rng.random() < 0.7 and wing_back > 4:
        y = rng.uniform(3, min(wing_back - 1, 6))
        points = [
            (root_x, y),
            (root_x - span, y - span * 0.6),
            (root_x - span, y - span * 0.6 - 1),
            (root_x, y - rng.uniform(1.5, 3)),
        ]
        cv.polygon(points, "w", "both")
    elif front + 3 < cv.h - 2:
        y = rng.uniform(front + 2, cv.h - 2)
        span *= 0.7
        cv.polygon(
            [(root_x, y), (root_x - span, y - span * 0.5), (root_x - span, y - span * 0.5 - 1), (root_x, y - 2)],
            "w",
            "both",
        )


def _fins(rng: Rng, cv: Canvas, body: float) -> None:
    """Thin raised fins on the tail: one in the middle, or two."""
    middle, length = cv.w // 2, rng.randint(2, 4)
    columns = [middle] if rng.random() < 0.5 else [middle - round(body) - 1, middle + round(body) + 1]
    for x in columns:
        cv.line(x, 0, x, length, "S")


def _pods_and_weapons(rng: Rng, cv: Canvas, root_x: float, front: float) -> None:
    """Slim engine pods under the wings, weapons pointing forward from them."""
    if rng.random() < 0.3 and root_x > 4:
        x = round(root_x * rng.uniform(0.4, 0.65))
        pod_front = round(front - (cv.w // 2 - x) * 0.3)
        cv.rect(x, x, pod_front - rng.randint(3, 5), pod_front, "N", "both")
    if rng.random() < 0.5 and root_x > 3:
        x = round(root_x * rng.uniform(0.2, 0.5))
        edge = next((y for y in range(cv.h - 1, -1, -1) if cv.get(x, y) in "wW"), None)
        if edge is not None:
            cv.line(x, edge - 1, x, min(cv.h - 1, edge + rng.randint(1, 2)), "r", "both")


# Industrial ships: a core hull around column `mx`, `half` wide on each side.


def core_spindle(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    cv.polygon([(mx - half, 0), (mx + half, 0), (mx + 0.6, cv.h - 0.5), (mx - 0.6, cv.h - 0.5)], "h")


def core_block(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    cut, bottom = rng.randint(1, 3), cv.h - 1
    cv.polygon(
        [(mx - half, cut), (mx - half + cut, 0), (mx + half - cut, 0), (mx + half, cut), (mx + half, bottom - cut),
         (mx + half - cut, bottom), (mx - half + cut, bottom), (mx - half, bottom - cut)],
        "h",
    )  # fmt: skip


def core_wedge(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # narrow at the back, wide at the front
    cv.polygon([(mx - 1, 0), (mx + 1, 0), (mx + half, cv.h * 0.8), (mx, cv.h - 0.5), (mx - half, cv.h * 0.8)], "h")


def core_egg(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    cv.ellipse(mx, cv.h / 2, half + 0.4, cv.h / 2 - 0.3, "h")


def core_segmented(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # blocks of different widths, joined by a neck
    count = rng.randint(2, 4)
    length = cv.h / count
    for i in range(count):
        width = rng.uniform(max(1.0, half * 0.5), half)
        cv.rect(mx - width, mx + width, i * length + (0.8 if i else 0), (i + 1) * length - 1, "h")
    cv.rect(mx - 1, mx + 1, 0, cv.h - 1, "h")


def core_cross(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    arm = rng.uniform(0.35, 0.6) * cv.h
    cv.rect(mx - max(1, half // 3), mx + max(1, half // 3), 0, cv.h - 1, "h")
    cv.rect(mx - half, mx + half, arm - 1.5, arm + 1.5, "h")


def core_crescent(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # horns reaching forward
    cv.ellipse(mx, cv.h * 0.35, half + 0.4, cv.h * 0.35, "h")
    cv.ellipse(mx, cv.h * 0.75, half * 0.55, cv.h * 0.45, ".")
    cv.rect(mx - 1, mx + 1, 0, cv.h * 0.5, "h")


def core_frame(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # an open frame around a thin core
    cv.rect(mx - half, mx + half, 1, cv.h - 2, "N")
    cv.rect(mx - half + 2, mx + half - 2, 3, cv.h - 4, ".")
    cv.rect(mx - 1, mx + 1, 0, cv.h - 1, "h")


def core_diamond(rng: Rng, cv: Canvas, mx: int, half: int) -> None:
    middle = cv.h * rng.uniform(0.35, 0.6)
    cv.polygon([(mx, -0.5), (mx + half + 0.5, middle), (mx, cv.h - 0.5), (mx - half - 0.5, middle)], "h")


def core_arrow(rng: Rng, cv: Canvas, mx: int, half: int) -> None:  # an arrowhead with a notched back
    notch = rng.uniform(0.2, 0.4) * cv.h
    cv.polygon([(mx - half, 0), (mx, notch), (mx + half, 0), (mx + 0.8, cv.h - 0.5), (mx - 0.8, cv.h - 0.5)], "h")


CORES = [core_spindle, core_block, core_wedge, core_egg, core_segmented, core_cross, core_crescent, core_frame,
         core_diamond, core_arrow]  # fmt: skip


# Attachments, on the left of the core (`edge`: its outer column), or on both sides.


def wing_delta(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    root, tip = rng.uniform(0.15, 0.45) * cv.h, rng.uniform(0.6, 0.95) * cv.h
    cv.polygon([(edge + 0.5, root), (0, tip), (0, min(cv.h - 1, tip + 2)), (edge + 0.5, tip + 1)], "w", side)


def wing_swept(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    root = rng.uniform(0.35, 0.65) * cv.h
    sweep = rng.uniform(-0.35, 0.35) * cv.h  # back (up) or forward (down)
    chord = rng.randint(2, 4)
    tip = max(1.0, chord * rng.uniform(0.3, 0.6))  # narrower at the tip
    cv.polygon(
        [(edge + 0.5, root), (0, root + sweep), (0, root + sweep + tip), (edge + 0.5, root + chord + 1)], "w", side
    )
    if rng.random() < 0.5:
        cv.rect(0, 1, root + sweep - 1, root + sweep + chord, "N", side)  # a pod on the tip


def wing_straight(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    y, chord = rng.uniform(0.3, 0.7) * cv.h, rng.randint(2, 4)
    tip = max(1.0, chord * rng.uniform(0.3, 0.6))
    shift = (chord - tip) * 0.7
    cv.polygon([(edge + 0.5, y), (-0.5, y + shift), (-0.5, y + shift + tip), (edge + 0.5, y + chord)], "w", side)


def nacelle(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x = rng.randint(0, max(0, edge - 3))
    top, length = rng.uniform(0, 0.3) * cv.h, rng.uniform(0.35, 0.8) * cv.h
    width = rng.randint(1, 3)
    cv.rect(x, x + width, top, top + length, "N", side)
    cv.rect(x + width, edge, top + length * 0.4, top + length * 0.4 + 1, "w", side)  # its pylon


def boom(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x = rng.randint(0, max(0, edge - 2))
    cv.line(edge, rng.uniform(0.4, 0.8) * cv.h, x, rng.uniform(0, 0.25) * cv.h, "N", side)
    cv.rect(x - 1, x + 1, 0, rng.randint(2, 4), "h", side)  # an engine pod at its end


def mandible(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x = max(0, edge - rng.randint(0, 2))
    start = rng.uniform(0.4, 0.65) * cv.h
    cv.polygon(
        [(x - 1, start), (x + 1.5, start), (x + rng.uniform(1, 3), cv.h - 0.5), (x - 0.5, cv.h - 1.5)], "N", side
    )


def fins(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    tip = max(0, edge - rng.randint(2, 5))
    cv.polygon([(edge + 0.5, 1), (tip, -0.5), (tip, 1.5), (edge + 0.5, 4)], "w", side)


def turret(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    x, y = rng.randint(max(0, edge - 3), max(0, edge)), rng.uniform(0.2, 0.8) * cv.h
    cv.rect(x - 1, x + 1, y - 1, y + 1, "t", side)
    cv.line(x, y + 1, x, min(cv.h - 1, y + rng.randint(2, 5)), "r", side)  # its barrel


def cannon(rng: Rng, cv: Canvas, edge: int, side: str) -> None:  # a big gun along the flank
    x = rng.randint(max(0, edge - 2), max(0, edge))
    cv.rect(x - 1, x + 1, rng.uniform(0.1, 0.4) * cv.h, cv.h * 0.75, "t", side)
    cv.line(x, cv.h * 0.75, x, cv.h - 1, "r", side)


def containers(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    width = rng.randint(2, 3)
    x, y = max(0, edge - width), rng.uniform(0.05, 0.3) * cv.h
    while y < cv.h * 0.8:
        size = rng.randint(2, 4)
        cv.rect(x, x + width - 1, y, y + size - 1, "t", side)
        y += size + 1


def radiator(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    y, length, width = rng.uniform(0.1, 0.5) * cv.h, rng.randint(3, 7), rng.randint(2, max(2, edge))
    for i in range(length):
        cv.rect(edge - width, edge, y + i, y + i, "W" if i % 2 else "w", side)


def antenna(rng: Rng, cv: Canvas, edge: int, side: str) -> None:
    cv.line(edge, rng.uniform(0.3, 0.7) * cv.h, max(0, edge - rng.randint(3, 7)), rng.uniform(0, cv.h), "r", side)


ATTACHMENTS = [wing_delta, wing_swept, wing_straight, nacelle, boom, mandible, fins, turret, cannon, containers,
               radiator, antenna]  # fmt: skip


def industrial(rng: Rng, lopsided: bool) -> tuple[Canvas, bool]:
    kind = rng.random()
    if kind < 0.2:  # small drones and fighters
        width, height = rng.randrange(7, 14, 2), rng.randint(7, 13)
    elif kind < 0.8:
        width, height = rng.randrange(13, 24, 2), rng.randint(11, 22)
    else:  # heavies
        width, height = rng.randrange(23, 36, 2), rng.randint(19, 34)
    cv = Canvas(width, height)
    mx = width // 2 + (rng.choice((-1, 1)) * rng.randint(0, max(1, width // 6)) if lopsided else 0)
    half = max(1, round(width * rng.uniform(0.12, 0.3)))
    rng.choice(CORES)(rng, cv, mx, half)
    edge = max(1, mx - half - 1)
    for _ in range(rng.randint(1, 3 if width > 12 else 2)):
        side = "one" if lopsided and rng.random() < 0.6 else "both"
        rng.choice(ATTACHMENTS)(rng, cv, edge, side)
    if lopsided and rng.random() < 0.5:  # so lopsided ships lean either way
        cv.cells = [row[::-1] for row in cv.cells]
    return cv, not lopsided


# Details, on every ship.


def trim(cv: Canvas, symmetric: bool, also: Canvas | None = None) -> None:
    """Drop the empty rows and columns around the ship (a symmetric one stays centred); `also` is cropped the same
    way.
    """
    rows = [y for y in range(cv.h) if any(cv.filled(x, y) for x in range(cv.w))]
    columns = [x for x in range(cv.w) if any(cv.filled(x, y) for y in range(cv.h))]
    if not rows or not columns:
        return
    left, right = columns[0], columns[-1]
    if symmetric:
        left = min(left, cv.w - 1 - right)
        right = cv.w - 1 - left
    for canvas in [cv] + ([also] if also is not None else []):
        canvas.cells = [row[left : right + 1] for row in canvas.cells[rows[0] : rows[-1] + 1]]
        canvas.h, canvas.w = len(canvas.cells), len(canvas.cells[0])


def detail(rng: Rng, cv: Canvas, symmetric: bool) -> list[dict]:
    """Bands, panel lines, plates, a spine, the cockpit and sensor, markings, guns, nozzles; the engines' flames. A
    symmetric ship gets them on its left half, mirrored.
    """
    _bands(rng, cv)
    _wing_edges(cv)
    _panel_lines(rng, cv)
    _plates(rng, cv)
    spine = cv.w // 2 if symmetric else _thickest_column(cv)
    if rng.random() < 0.7:
        for x, y in cv.cells_of("hHk"):
            if x == spine:
                cv.set(x, y, "S")
    if rng.random() < 0.35:
        _livery(rng, cv)
    _cockpit(rng, cv, spine, symmetric)
    _markings(rng, cv)
    _guns(rng, cv)
    _nozzles(rng, cv, spine, symmetric)
    if symmetric:
        for row in cv.cells:
            for x in range(cv.w // 2):
                row[cv.w - 1 - x] = row[x]
    width, length = rng.choice((2.0, 2.4, 3.0)), rng.randint(4, 8)
    return [{"x": x, "y": y, "width": width, "length": length, "towards": "top"} for x, y in cv.cells_of("o")]


def _bands(rng: Rng, cv: Canvas) -> None:
    band = rng.randint(2, 4)
    for x, y in cv.cells_of("hw"):
        if cv.get(x, y) == "h" and y % band == 0:
            cv.set(x, y, "H")
        elif cv.get(x, y) == "w" and (x + y) % 4 == 0:
            cv.set(x, y, "W")


def _wing_edges(cv: Canvas) -> None:
    """A light leading edge (towards the nose), a dark line of flaps at the back."""
    for x, y in cv.cells_of("wW"):
        if not cv.filled(x, y + 1):
            cv.set(x, y, "W")
        elif not cv.filled(x, y - 1) and cv.get(x, y + 1) in "wW":
            cv.set(x, y, "k")


def _panel_lines(rng: Rng, cv: Canvas) -> None:
    rows = set(range(2, cv.h - 2, rng.randint(3, 5)))
    for x, y in cv.cells_of("hH"):
        if y in rows and cv.filled(x, y - 1) and cv.filled(x, y + 1):
            cv.set(x, y, "k")


def _plates(rng: Rng, cv: Canvas) -> None:
    """Heavy plates along the hull's sides."""
    for x, y in cv.cells_of("hH"):
        if (not cv.filled(x - 1, y) or not cv.filled(x + 1, y)) and rng.random() < 0.6:
            cv.set(x, y, "N")


def _thickest_column(cv: Canvas) -> int:
    counts = [sum(cv.get(x, y) in HULL for y in range(cv.h)) for x in range(cv.w)]
    return max(range(cv.w), key=lambda x: (counts[x], -abs(x - cv.w // 2)))


def _livery(rng: Rng, cv: Canvas) -> None:
    """A painted band across the hull."""
    top = rng.randint(0, max(0, cv.h // 2))
    bottom = top + rng.randint(2, 5)
    for x, y in cv.cells_of("hH"):
        if top <= y < bottom:
            cv.set(x, y, "L")


def _cockpit(rng: Rng, cv: Canvas, spine: int, symmetric: bool) -> None:
    nose = max((y for y in range(cv.h) if cv.filled(spine, y)), default=cv.h - 1)
    offset = 0 if symmetric or rng.random() < 0.5 else rng.choice((-1, 1)) * rng.randint(1, 2)  # off-centre
    y = max(0, nose - rng.randint(1, max(1, min(5, cv.h // 3))))
    size = 1 if cv.w < 11 else rng.randint(1, 2)
    for cy in range(y - size + 1, y + 1):
        for cx in range(spine + offset - (size - 1), spine + offset + size):
            if cv.filled(cx, cy):
                cv.set(cx, cy, "c")
    if cv.filled(spine + offset, y):
        cv.set(spine + offset, y, "R")


def _markings(rng: Rng, cv: Canvas) -> None:
    """The accent color: on the wings' edges (as thin as the wing), and on a few plates."""
    for x, y in cv.cells_of("wW"):
        if (not cv.filled(x - 1, y) or not cv.filled(x + 1, y)) and y % 3 == 0:
            cv.set(x, y, "q")
    plates = cv.cells_of("N")
    for x, y in rng.sample(plates, min(len(plates), rng.randint(1, 4))):
        cv.set(x, y, "p")


def _guns(rng: Rng, cv: Canvas) -> None:
    """Barrels pointing down (forward) from the front of the ship."""
    for _ in range(rng.randint(0, 2)):
        x = rng.randrange(cv.w)
        bottom = max((y for y in range(cv.h) if cv.filled(x, y)), default=cv.h - 1)
        for y in range(bottom + 1, min(cv.h, bottom + rng.randint(2, 3) + 1)):
            cv.set(x, y, "r")


def _nozzles(rng: Rng, cv: Canvas, spine: int, symmetric: bool) -> None:
    """On the backmost hull cells: 1 to 4 of them, spread out (a symmetric ship's on its left half)."""
    backs = []
    for x in range(cv.w if not symmetric else (cv.w - 1) // 2 + 1):
        top = next((y for y in range(cv.h) if cv.filled(x, y)), None)
        if top is not None and cv.get(x, top) in HULL + "wW" and top <= cv.h // 2:
            backs.append((top, x))
    chosen: list[tuple[int, int]] = []
    wanted = rng.randint(1, 4)
    for top, x in sorted(backs):
        if len(chosen) < wanted and all(abs(x - other) >= 3 for _, other in chosen):
            chosen.append((top, x))
    if not chosen:  # nothing at the back to put one on: the spine's first cell
        chosen = [(next(y for y in range(cv.h) if cv.filled(spine, y)), spine)]
    for top, x in chosen:
        cv.set(x, top, "o")


def industrial_shaping(cv: Canvas) -> Shaping:
    """How an industrial ship's plan becomes 3D: its hull thicker on bigger ships."""
    top = max(1, min(4, round(min(cv.w, cv.h) * 0.16)))
    return Shaping(
        roles={
            "S": "raised",
            "c": "raised",
            "R": "raised",
            "k": "seam",
            "w": "wing",
            "W": "wing",
            "q": "wing",
            "t": "pod",
            "r": "gun",
        },
        tiers={"S": 1, "c": 1, "R": 2},
        top=top,
        bottom=max(1, top - 1),
        pod=max(1, top - 1),
    )


def palette(rng: Rng, used: set[str]) -> dict:
    tint = HULL_TINTS[rng.choice(list(HULL_TINTS))]
    marking, sensor = ACCENTS[rng.choice(list(ACCENTS))]
    entries: dict[str, tuple[tuple[float, ...], int]] = {
        char: (tuple(round(min(1.0, c * t), 3) for c, t in zip(color, tint, strict=True)), height)
        for char, (color, height) in GREYS.items()
    }
    entries["c"] = COCKPIT
    entries["p"] = (marking, 3)
    entries["q"] = (marking, 1)  # on wings: as thin as them
    entries["R"] = (sensor, 5)
    entries["L"] = (rng.choice(LIVERIES), 3)
    entries["D"] = (tuple(round(c * UNDERSIDE, 3) for c in entries["h"][0]), 1)  # the underside (3D ships only)
    return {char: {"color": list(color), "height": height} for char, (color, height) in entries.items() if char in used}


def features(rows: list[str], symmetric: bool) -> list[float]:
    """For telling ships apart: the outline shrunk to 8 x 8, the size, the proportions, symmetry, how full."""
    height, width = len(rows), len(rows[0])
    grid = []
    for gy in range(8):
        for gx in range(8):
            y0, x0 = gy * height // 8, gx * width // 8
            y1, x1 = max(y0 + 1, (gy + 1) * height // 8), max(x0 + 1, (gx + 1) * width // 8)
            cells = [rows[y][x] != "." for y in range(y0, y1) for x in range(x0, x1)]
            grid.append(sum(cells) / len(cells))
    filled = sum(char != "." for row in rows for char in row) / (width * height)
    return [*grid, 3 * width / 35, 3 * height / 35, 2 * math.log(width / height), 0.4 * (not symmetric), 2 * filled]


def ship(rng: Rng, group: str) -> tuple[list[float], Callable[[], dict]] | None:
    """One ship of a group ("aircraft", "symmetric" or "lopsided"): its features, and what makes its drawing (only
    the ships kept are built in 3D).
    """
    parts: Parts | None = None
    if group == "aircraft":
        cv, symmetric, parts = aircraft(rng)
    else:
        cv, symmetric = industrial(rng, group == "lopsided")
    trim(cv, symmetric, parts)
    if cv.w < 5 or cv.h < 5:
        return None
    engines = detail(rng, cv, symmetric)
    rows = cv.rows()
    colors = palette(rng, {char for row in rows for char in row} | {"D", "h"})  # underside, under raised cells

    def make() -> dict:
        if parts is not None:
            return {**layered_drawing(aircraft_layers(cv, parts), cv, colors), "engines": engines}
        cells, heights = sculpt(cv, industrial_shaping(cv))
        return {**layered_drawing(cells, cv, colors), "engines": engines_at_height(engines, heights)}

    return features(rows, symmetric), make


def most_different(pool: list[tuple[list[float], T]], count: int) -> list[T]:
    """`count` things of the pool, by their features: each next one is the farthest from all those already kept."""
    kept = [0]
    distance = [math.dist(f, pool[0][0]) for f, _ in pool]
    while len(kept) < min(count, len(pool)):
        index = max(range(len(pool)), key=distance.__getitem__)
        kept.append(index)
        distance = [min(d, math.dist(f, pool[index][0])) for d, (f, _) in zip(distance, pool, strict=True)]
    return [pool[index][1] for index in kept]


def generate(count: int, kind: str, seed: int, pool_factor: int) -> list[dict]:
    rng = random.Random(seed)  # noqa: S311 - drawings, not cryptography
    drawings = []
    shares = MIXES[kind]
    for index, (group, share) in enumerate(shares.items()):
        wanted = count - len(drawings) if index == len(shares) - 1 else round(count * share)
        pool = [made for _ in range(wanted * pool_factor) if (made := ship(rng, group)) is not None]
        if pool:
            drawings += [make() for make in most_different(pool, wanted)]
    rng.shuffle(drawings)
    return drawings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=500, help="how many to write (default 200)")
    parser.add_argument("--kind", choices=MIXES, default="all", help="aircraft, industrial or all (default)")
    parser.add_argument("--seed", type=int, help="the same seed makes the same batch (default: a new one)")
    parser.add_argument("--pool", type=int, default=7, help="how many generated for each one kept (default 7)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="where (default: the game's candidates)")
    parser.add_argument("--append", action="store_true", help="number after the ones there instead of replacing them")
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else int(time.time() * 1000) % 1_000_000
    args.out.mkdir(parents=True, exist_ok=True)
    existing = sorted(args.out.glob("*.json"))
    first = 1
    if args.append:
        first = max((int(path.stem) for path in existing if path.stem.isdigit()), default=0) + 1
    else:
        for path in existing:
            path.unlink()
    for number, drawing in enumerate(generate(args.count, args.kind, seed, args.pool), start=first):
        (args.out / f"{number:03d}.json").write_text(json.dumps(drawing, indent=2) + "\n")
    print(f"wrote {args.count} {args.kind} candidates ({first:03d} to {first + args.count - 1:03d}) to {args.out}")
    print(f"seed {seed}: --seed {seed} makes the same batch again")


if __name__ == "__main__":
    main()
