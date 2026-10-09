"""The hulls: profiles from the tail to the nose, made to any size; the catalog has each in six sizes.

A profile is a list of (share of the way from the tail to the nose, half width, height on top, depth underneath),
each a share of the hull's; between two points it goes straight. Its cross-section is round (an ellipse), boxy (flat
sides, the corners cut) or a diamond (a keel and a ridge). The hull is painted: plating with lighter bands, panel lines
across the top, a spine, plates on its sides, the underside darker. Small hulls also make pods and booms.
"""

import itertools
import math
from dataclasses import replace
from functools import cache

from pewpy.generators.models.parts.part import Part, Sketch

Profile = list[tuple[float, float, float, float]]

# By name: its profile, its cross-section, how long and how wide it is for its size (shares of SIZES'), what it is.
PROFILES: dict[str, tuple[Profile, str, float, float, str]] = {
    "dart": (
        [(0, 0.6, 0.55, 0.45), (0.2, 0.75, 0.8, 0.6), (0.5, 1, 1, 0.8), (0.78, 0.6, 0.75, 0.5), (1, 0.12, 0.2, 0.1)],
        "round", 1.0, 0.9, "a slim body, widest in its middle, a sharp nose",
    ),
    "cigar": (
        [(0, 0.55, 0.6, 0.6), (0.12, 0.9, 0.9, 0.9), (0.7, 1, 1, 1), (0.9, 0.7, 0.7, 0.7), (1, 0.25, 0.25, 0.25)],
        "round", 1.0, 0.8, "a long round tube, a blunt nose",
    ),
    "wedge": (
        [(0, 1, 0.7, 0.5), (0.35, 0.95, 1, 0.6), (0.75, 0.55, 0.7, 0.4), (1, 0.15, 0.3, 0.1)],
        "boxy", 0.95, 1.1, "wide at the back, narrowing to a point",
    ),
    "brick": (
        [(0, 0.85, 0.8, 0.7), (0.1, 1, 1, 0.8), (0.8, 1, 1, 0.8), (0.92, 0.85, 0.75, 0.6), (1, 0.6, 0.5, 0.4)],
        "boxy", 0.85, 1.15, "a heavy box, its corners cut",
    ),
    "bulb": (
        [(0, 0.5, 0.5, 0.4), (0.45, 0.5, 0.5, 0.4), (0.62, 0.85, 0.9, 0.8), (0.85, 1, 1, 0.9), (1, 0.5, 0.55, 0.45)],
        "round", 0.8, 1.0, "a thin tail and a big round head",
    ),
    "shark": (
        [(0, 0.3, 0.6, 0.3), (0.25, 0.7, 1, 0.5), (0.55, 1, 0.9, 0.6), (0.85, 0.75, 0.55, 0.45), (1, 0.35, 0.25, 0.2)],
        "round", 1.0, 1.0, "a humped back, a flat snout",
    ),
    "hammer": (
        [(0, 0.5, 0.6, 0.45), (0.55, 0.45, 0.7, 0.5), (0.7, 1, 0.75, 0.55), (0.92, 1, 0.6, 0.45), (1, 0.85, 0.4, 0.3)],
        "boxy", 0.95, 1.2, "a narrow body, a wide hammer head",
    ),
    "needle": (
        [(0, 0.5, 0.5, 0.45), (0.3, 0.8, 0.85, 0.7), (0.55, 1, 1, 0.8), (0.65, 0.45, 0.6, 0.4), (1, 0.12, 0.15, 0.12)],
        "round", 1.2, 0.75, "a body and a long needle nose",
    ),
    "manta": (
        [(0, 0.7, 0.4, 0.3), (0.3, 1, 0.75, 0.5), (0.7, 0.85, 1, 0.6), (1, 0.25, 0.35, 0.2)],
        "round", 0.8, 1.5, "flat and wide, a blended body",
    ),
    "arrow": (
        [(0, 0.9, 0.7, 0.5), (0.5, 0.75, 1, 0.6), (1, 0.08, 0.25, 0.1)],
        "boxy", 1.0, 1.0, "a straight taper from the tail to the tip",
    ),
    "spindle": (
        [(0, 0.2, 0.3, 0.3), (0.3, 0.8, 0.8, 0.8), (0.55, 1, 1, 1), (0.8, 0.75, 0.75, 0.75), (1, 0.1, 0.15, 0.15)],
        "round", 1.0, 0.85, "pointed at both ends",
    ),
    "lozenge": (
        [(0, 0.35, 0.4, 0.35), (0.5, 1, 1, 0.9), (1, 0.3, 0.35, 0.3)],
        "diamond", 0.9, 1.1, "a faceted diamond, a ridge on top and a keel below",
    ),
    "coffin": (
        [(0, 0.65, 0.8, 0.6), (0.65, 1, 1, 0.8), (1, 0.45, 0.6, 0.45)],
        "boxy", 0.9, 1.05, "a long six-sided box",
    ),
    "teardrop": (
        [(0, 0.15, 0.25, 0.25), (0.6, 1, 1, 1), (0.85, 0.85, 0.85, 0.85), (1, 0.35, 0.4, 0.4)],
        "round", 0.85, 1.05, "a drop, round in front and thin at the back",
    ),
    "blade": (
        [(0, 0.8, 0.4, 0.3), (0.4, 1, 0.55, 0.4), (0.8, 0.6, 0.4, 0.3), (1, 0.05, 0.15, 0.1)],
        "diamond", 1.1, 1.1, "flat and sharp, a low ridge",
    ),
    "keel": (
        [(0, 0.7, 0.6, 1), (0.4, 0.9, 0.8, 1), (0.8, 0.6, 0.6, 0.8), (1, 0.2, 0.3, 0.3)],
        "diamond", 1.0, 0.9, "a deep keel underneath",
    ),
}  # fmt: skip
SIZES = {  # (length, half width, height) of a profile's hull, before its own shares
    "tiny": (5, 1.1, 1.0),
    "small": (8, 1.6, 1.4),
    "medium": (13, 2.6, 2.0),
    "large": (20, 3.8, 2.6),
    "huge": (29, 5.2, 3.2),
    "colossal": (40, 7.0, 4.0),
}


def hull(name: str, size: str) -> Part:
    """Return a profile's hull of one of the catalog's sizes: see PROFILES and SIZES."""
    _, _, long, wide, what = PROFILES[name]
    base_length, base_half, height = SIZES[size]
    made = hull_at(name, max(4, round(base_length * long)), round(base_half * wide, 2), height)
    return replace(made, name=f"{name} hull, {size}", description=f"A {size} hull: {what}.")


TALLEST = 8.0  # cubes: the highest a hull gets on top, however wide (a boss's hull stays a hull) *(placeholder)*


def thickness(half: float) -> float:
    """Return how high a hull `half` cubes from its axis to its side is on top: as the catalog's sizes are, at most
    TALLEST.
    """  # noqa: D205 - the summary needs two lines
    return round(min(TALLEST, 0.9 * max(0.5, half) ** 0.75), 2)


@cache
def hull_at(name: str, length: int, half: float, height: float) -> Part:
    """Build a profile's hull of any size: `length` rows, `half` cubes from its axis to its side at its widest,
    `height` cubes high on top at its highest (see `thickness`). Made once for each size.
    """  # noqa: D205 - the summary needs two lines
    profile, section, _, _, what = PROFILES[name]
    sketch = Sketch()
    for y in range(length):
        _, w, top, bottom = _along(profile, y / (length - 1))
        w = max(0.5, w * half)
        top_z, bottom_z = max(0, round(top * height)), -max(0, round(bottom * height * 0.75))
        for x in range(round(w) + 1):
            low, high = _section(section, x / (w + 0.5), x >= round(w) and w >= 1.5, top_z, bottom_z)
            for z in range(low, high + 1):
                sketch.put(x, y, z, _paint(x, y, z, high, length, round(w), spine=section != "boxy"))
    return sketch.part(f"{name} hull, {length} long", "hull", "hull", f"A hull {length} cubes long: {what}.")


def _section(section: str, across: float, edge: bool, top: int, bottom: int) -> tuple[int, int]:
    """Return the lowest and highest z of a column `across` of the way out (0 its middle, 1 its side)."""
    if section == "round":
        shrink = math.sqrt(max(0.0, 1 - across * across))
        return round(bottom * shrink), round(top * shrink)
    if section == "diamond":
        shrink = max(0.0, 1 - across)
        return min(0, round(bottom * shrink)), max(0, round(top * shrink))
    cut = 1 if edge else 0
    return bottom + cut, top - cut


def _paint(x: int, y: int, z: int, top: int, length: int, side: int, *, spine: bool) -> str:
    """Return a hull cube's color: lighter bands, panel lines, a spine on top; plates on the sides; under, darker."""
    if z < 0:
        return "D"
    if z == top:
        if spine and x == 0:
            return "S"
        if 1 < y < length - 2 and y % 4 == 0:
            return "k"
        return "H" if y % 3 == 0 else "h"
    if x == side and y % 3 == 0:
        return "N"
    return "h"


def _along(profile: Profile, share: float) -> tuple[float, float, float, float]:
    """Return the profile at a share of the hull's length, going straight between its points."""
    pairs = list(itertools.pairwise(profile))
    (s0, *a), (s1, *b) = next((pair for pair in pairs if share <= pair[1][0]), pairs[-1])  # the stretch it's on
    t = (share - s0) / (s1 - s0) if s1 > s0 else 0.0
    w, top, bottom = (low + (high - low) * t for low, high in zip(a, b, strict=True))
    return share, w, top, bottom


def hulls() -> list[Part]:
    """Return every hull: each profile in each size."""
    return [hull(name, size) for name in PROFILES for size in SIZES]
