"""The hulls: hardcoded profiles from the tail to the nose, stretched to the ship's length, width and height.

A profile is a list of (share of the way from the tail to the nose, half width, height on top, depth underneath),
each a share of the hull's; between two points it goes straight. Its cross-section is round (an ellipse) or boxy
(flat sides, the corners cut). The hull is painted: plating with lighter bands, panel lines across the top, a
spine, the underside darker.
"""

import itertools
import math
from dataclasses import dataclass

from pewpy.tools.candidates.kit.ship import Ship
from pewpy.tools.common.geometry import Rng

Profile = list[tuple[float, float, float, float]]

HULLS: dict[str, tuple[Profile, str]] = {  # by name: its profile, its cross-section
    "dart": (
        [(0, 0.6, 0.55, 0.45), (0.2, 0.75, 0.8, 0.6), (0.5, 1, 1, 0.8), (0.78, 0.6, 0.75, 0.5), (1, 0.12, 0.2, 0.1)],
        "round",
    ),
    "cigar": (
        [(0, 0.55, 0.6, 0.6), (0.12, 0.9, 0.9, 0.9), (0.7, 1, 1, 1), (0.9, 0.7, 0.7, 0.7), (1, 0.25, 0.25, 0.25)],
        "round",
    ),
    "wedge": ([(0, 1, 0.7, 0.5), (0.35, 0.95, 1, 0.6), (0.75, 0.55, 0.7, 0.4), (1, 0.15, 0.3, 0.1)], "boxy"),
    "brick": (
        [(0, 0.85, 0.8, 0.7), (0.1, 1, 1, 0.8), (0.8, 1, 1, 0.8), (0.92, 0.85, 0.75, 0.6), (1, 0.6, 0.5, 0.4)],
        "boxy",
    ),
    "bulb": (
        [(0, 0.5, 0.5, 0.4), (0.45, 0.5, 0.5, 0.4), (0.62, 0.85, 0.9, 0.8), (0.85, 1, 1, 0.9), (1, 0.5, 0.55, 0.45)],
        "round",
    ),
    "shark": (
        [(0, 0.3, 0.6, 0.3), (0.25, 0.7, 1, 0.5), (0.55, 1, 0.9, 0.6), (0.85, 0.75, 0.55, 0.45), (1, 0.35, 0.25, 0.2)],
        "round",
    ),
    "hammer": (
        [(0, 0.5, 0.6, 0.45), (0.55, 0.45, 0.7, 0.5), (0.7, 1, 0.75, 0.55), (0.92, 1, 0.6, 0.45), (1, 0.85, 0.4, 0.3)],
        "boxy",
    ),
    "needle": (
        [(0, 0.5, 0.5, 0.45), (0.3, 0.8, 0.85, 0.7), (0.55, 1, 1, 0.8), (0.65, 0.45, 0.6, 0.4), (1, 0.12, 0.15, 0.12)],
        "round",
    ),
    "manta": ([(0, 0.7, 0.4, 0.3), (0.3, 1, 0.75, 0.5), (0.7, 0.85, 1, 0.6), (1, 0.25, 0.35, 0.2)], "round"),
    "arrow": ([(0, 0.9, 0.7, 0.5), (0.5, 0.75, 1, 0.6), (1, 0.08, 0.25, 0.1)], "boxy"),
    "spindle": (
        [(0, 0.2, 0.3, 0.3), (0.3, 0.8, 0.8, 0.8), (0.55, 1, 1, 1), (0.8, 0.75, 0.75, 0.75), (1, 0.1, 0.15, 0.15)],
        "round",
    ),
}


@dataclass
class Hull:
    """A hull placed on a ship: its size, and its half width, top and bottom on each row (y from the tail)."""

    length: int
    rows: list[tuple[float, int, int]]  # (half width, top z, bottom z) by y

    def half(self, y: int) -> float:
        """Return the hull's half width on row y (0 off the hull)."""
        return self.rows[y][0] if 0 <= y < self.length else 0.0

    def top_at(self, y: int) -> int:
        """Return the z of the hull's top on its axis on row y."""
        return self.rows[max(0, min(self.length - 1, y))][1]

    def bottom_at(self, y: int) -> int:
        """Return the z of the hull's bottom on its axis on row y."""
        return self.rows[max(0, min(self.length - 1, y))][2]

    def widest(self, low: float = 0.0, high: float = 1.0) -> int:
        """Return the row where the hull is widest, between two shares of its length."""
        first, last = round(low * (self.length - 1)), round(high * (self.length - 1))
        return max(range(first, last + 1), key=lambda y: (self.rows[y][0], -abs(y - (first + last) / 2)))


def hull(
    rng: Rng, ship: Ship, name: str, length: int, half: float, height: float, *, offset: int = 0, back: int = 0
) -> Hull:
    """Build a hull of `length` rows, `half` cubes from its axis to its side at the widest, `height` thick on top.

    On the ship's axis, or (`offset` cubes from it) a pair of booms, one on each side; its tail on row `back`. The rows
    of the returned Hull count from its own tail.
    """
    profile, section = HULLS[name]
    rows = []
    for y in range(length):
        share = y / max(1, length - 1)
        _, w, top, bottom = _along(profile, share)
        rows.append((max(0.5, w * half), max(0, round(top * height)), -max(0, round(bottom * height * 0.75))))
    band, lines = rng.randint(2, 4), rng.randint(3, 5)
    spine = rng.random() < 0.6
    for y, (w, top, bottom) in enumerate(rows):
        for dx in range(-round(w) if offset else 0, round(w) + 1):
            x = abs(dx)
            across = x / (w + 0.5)
            if section == "round":
                shrink = math.sqrt(max(0.0, 1 - across * across))
                z_top, z_bottom = round(top * shrink), round(bottom * shrink)
            else:
                cut = 1 if x >= round(w) and w >= 1.5 else 0
                z_top, z_bottom = top - cut, bottom + cut
            for z in range(z_bottom, z_top + 1):
                char = "D" if z < 0 else "h"
                if z == z_top:
                    char = "H" if y % band == 0 else "h"
                    if 1 < y < length - 2 and y % lines == 0:
                        char = "k"
                    if spine and x == 0:
                        char = "S"
                elif z >= 0 and x == round(w) and y % band == 0:
                    char = "N"  # plates on the sides
                ship.put(-x if not offset else -offset + dx, back + y, z, char)
    return Hull(length, rows)


def _along(profile: Profile, share: float) -> tuple[float, float, float, float]:
    """Return the profile at a share of the hull's length, going straight between its points."""
    for (s0, *a), (s1, *b) in itertools.pairwise(profile):
        if s0 <= share <= s1:
            t = (share - s0) / (s1 - s0) if s1 > s0 else 0.0
            w, top, bottom = (low + (high - low) * t for low, high in zip(a, b, strict=True))
            return share, w, top, bottom
    return profile[-1]
