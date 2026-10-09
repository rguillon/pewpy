"""The wings: outlines of a left wing, each in six sizes (its span and its root's chord).

An outline is a polygon of (share of the span from the root to the tip, share of the root's chord from its trailing
edge towards the nose). A wing is one cube thick (two at its root), rises or droops towards its tip, and is painted: a
light leading edge, dark flaps along the trailing edge, panels, a marking on its tip. The right wing is its mirror
image.
"""

from pewpy.generators.models.common.geometry import Point, inside
from pewpy.generators.models.ships.parts.part import Part, Sketch

# By name: its outline, how much it rises (cubes up per cube out; below 0 it droops), what it is.
OUTLINES: dict[str, tuple[list[Point], float, str]] = {
    "swept": ([(0, 0), (0, 1), (1, 0.2), (1, -0.15)], 0.0, "swept back"),
    "delta": ([(0, -0.05), (0, 1.15), (1, 0.05), (1, -0.05)], 0.0, "a triangle"),
    "forward": ([(0, 0.05), (0, 0.85), (1, 1.2), (1, 0.85)], 0.0, "swept forward"),
    "straight": ([(0, 0), (0, 1), (1, 0.9), (1, 0.3)], 0.0, "straight, its tip rounded"),
    "cranked": ([(0, -0.05), (0, 1.15), (0.35, 0.85), (1, 0.15), (1, -0.05)], 0.0, "a delta with a crank"),
    "ogival": ([(0, -0.1), (0, 1.2), (0.3, 0.95), (0.65, 0.55), (1, 0.12), (1, -0.05)], 0.0, "a curved delta"),
    "bat": ([(0, 0), (0, 1), (1, 0.55), (1, 0.1), (0.7, 0.3), (0.4, 0.05)], 0.0, "scalloped behind"),
    "trapezoid": ([(0, 0), (0, 1), (1, 0.75), (1, 0.35)], 0.0, "tapered"),
    "scythe": ([(0, 0.1), (0, 1), (0.6, 0.75), (1, 0.15), (1, -0.25), (0.55, 0.2)], 0.0, "a hooked blade"),
    "box": ([(0, 0), (0, 1), (1, 1), (1, 0)], 0.0, "a plain slab"),
    "clipped": ([(0, -0.05), (0, 1.1), (0.8, 0.35), (1, 0.3), (1, -0.05)], 0.0, "a delta, its tip clipped"),
    "crescent": ([(0, 0), (0, 1), (0.5, 0.75), (1, 0.2), (1, -0.3), (0.5, -0.05)], 0.0, "a crescent, swept back"),
    "double_delta": ([(0, 0), (0, 1.4), (0.25, 0.75), (1, 0.1), (1, 0)], 0.0, "a long strake and a delta"),
    "stub": ([(0, 0.1), (0, 0.9), (1, 0.7), (1, 0.3)], 0.0, "short and thick"),
    "gull": ([(0, 0), (0, 1), (1, 0.6), (1, 0.05)], 0.35, "rising to its tip"),
    "anhedral": ([(0, 0), (0, 1), (1, 0.45), (1, -0.05)], -0.3, "drooping to its tip"),
}
SIZES = {  # (span, chord)
    "tiny": (1, 3),
    "small": (3, 4),
    "medium": (6, 6),
    "large": (10, 8),
    "huge": (15, 10),
    "giant": (21, 11),
}


def wing(name: str, size: str) -> Part:
    """Build a left wing (x <= 0) of an outline and a size: see OUTLINES and SIZES."""
    points, rise, what = OUTLINES[name]
    span, chord = SIZES[size]
    heights: dict[tuple[int, int], int] = {}
    for i in range(span + 1):
        for y in range(-chord, 2 * chord + 1):
            if inside((i + 0.5) / (span + 1), (y + 0.5) / chord, points):
                heights[i, y] = round(i * rise)
    tip = max(i for i, _ in heights)
    sketch = Sketch()
    for (i, y), z in heights.items():
        if (i, y + 1) not in heights:
            paint = "W"  # the leading edge
        elif (i, y - 1) not in heights:
            paint = "k"  # the flaps
        elif i >= tip - 1:
            paint = "q"  # the tip's marking
        else:
            paint = "w" if (i + y) % 4 else "W"
        inner = heights.get((i - 1, y), z)  # a step up or down: the cube beside it too, so they touch
        for level in range(min(z, inner) - (1 if i < 2 else 0), max(z, inner) + 1):
            sketch.put(-i, y, level, paint, mirror=False)
    return sketch.part(f"{name} wing, {size}", "wing", "wing", f"A {size} wing, {what}: {span + 1} cubes long.")


def wings() -> list[Part]:
    """Return every wing: each outline in each size."""
    return [wing(name, size) for name in OUTLINES for size in SIZES]
