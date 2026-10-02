"""Aircraft: a slender fuselage, thin wings (wings/: one module per plan), a tailplane or canards, fins, pods."""

import math

from pewpewdev.tools.candidates.aircraft.wings import WING_PLANS
from pewpewdev.tools.candidates.canvas import Canvas, Rng


class Parts(Canvas):
    """What each cell of an aircraft's drawing is, for building it in 3D (see `aircraft_layers`).

    "F" fuselage, "W" wing or tailplane, "V" upright fin, "P" engine pod, "G" gun.
    """


def aircraft(rng: Rng) -> tuple[Canvas, bool, Parts]:
    """Draw an aircraft: its plan, whether it's symmetric, and its parts."""
    small = rng.random() < 0.25
    width = rng.randrange(9, 16, 2) if small else rng.randrange(15, 32, 2)
    height = rng.randint(9, 15) if small else rng.randint(14, 30)
    cv, parts = Canvas(width, height), Parts(width, height)
    body = rng.choice((0.6, 1.0)) if small else rng.choice((0.6, 1.0, 1.0, 1.5, 2.0))
    fuselage(rng, cv, body)
    root_x = width // 2 - round(body) - 0.5
    plan = rng.choice(("swept", "swept", "delta", "cranked", "forward", "ogival", "straight"))
    front = height * rng.uniform(0.5, 0.72)  # the wing root's leading edge (towards the nose)
    points = WING_PLANS[plan](rng, height, root_x, front)
    cv.polygon(points, "w", "both")
    parts.polygon(points, "W", "both")
    if plan not in ("delta", "ogival") or rng.random() < 0.3:
        tail(rng, cv, root_x, front, min(y for _, y in points))
    for x, y in cv.cells_of("w"):
        parts.set(x, y, "W")  # the tailplane too
    for x, y in cv.cells_of("h"):
        parts.set(x, y, "F")  # the fuselage, over the wings' roots
    fin(rng, cv, body)
    for x, y in cv.cells_of("S"):
        parts.set(x, y, "V")
    pods_and_weapons(rng, cv, root_x, front)
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
    """Build the aircraft in 3D: (column, row, layer) -> its drawing's character.

    Layers are counted from the middle plane, negative ones up towards the camera. A round fuselage (its width on the
    drawing gives its depth), a canopy on top of it, thin wings and tailplanes rising a little towards their tips,
    upright fins, pods and guns slung underneath.
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


def fuselage(rng: Rng, cv: Canvas, body: float) -> None:
    """Draw the fuselage: a thin tail at the back, full width in the middle, an ogive nose."""
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


def tail(rng: Rng, cv: Canvas, root_x: float, front: float, wing_back: float) -> None:
    """Draw a small swept tailplane at the back, or canards near the nose."""
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


def fin(rng: Rng, cv: Canvas, body: float) -> None:
    """Thin raised fins on the tail: one in the middle, or two."""
    middle, length = cv.w // 2, rng.randint(2, 4)
    columns = [middle] if rng.random() < 0.5 else [middle - round(body) - 1, middle + round(body) + 1]
    for x in columns:
        cv.line(x, 0, x, length, "S")


def pods_and_weapons(rng: Rng, cv: Canvas, root_x: float, front: float) -> None:
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
