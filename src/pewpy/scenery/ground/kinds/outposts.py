"""Outposts: small compounds (airfields, radar stations, factories, depots, sci-fi colonies) on any ground.

They are set where the ground is flattest (and dry, over a fluid); some on a concrete apron, the others straight on
the ground.

The ground under a compound is levelled, blending back into the land around it: a clearing in a forest, a terrace on
a mountainside, land won from the water. On a settlement, a compound takes the place of what stood there (see
`clear`). Its lot is cut into a few smaller ones: the compound's main buildings take the first, the rest pick among
its others. props/ builds each prop. Positions are in world units, x from the ground's left edge, y down the loop,
like the relief's grid. Independent from Panda3D.
"""

import math
import random
from dataclasses import replace

import numpy as np

from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.ground.settlement import SURFACE_STEP, Layout, Prop, Rect, Surface, lots, shrink
from pewpy.scenery.params import Outposts

APRON_HEIGHT = 0.003
BLEND = 0.06  # the levelled ground blends back into the land around it over this distance
TRIES = 40  # places tried for each compound: the flattest wins
DRY = 0.006  # over a fluid, the levelled ground is at least this high
LEVEL_AT = 30  # the levelled ground's height: this percentile of the ground's under the compound (cut, not filled)
SMALLEST_LOT = 0.06
PAVED_SHARE = 0.35  # the compounds on a concrete apron; the others stand on the bare (levelled) ground...
EMPTY_LOTS = 0.35  # ...with this share of their lots (but the main buildings') left empty

# Each compound: its main buildings (one in each of the first lots), then what the other lots pick among.
COMPOUNDS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "airfield": (("hangar", "pad"), ("hangar", "containers", "antenna", "tank", "warehouse", "pad")),
    "radar_station": (("radar", "antenna"), ("radar", "dome", "warehouse", "containers", "antenna")),
    "factory": (("warehouse", "warehouse"), ("containers", "tank", "stack", "warehouse", "hangar")),
    "depot": (("containers", "warehouse"), ("containers", "containers", "tank", "antenna", "hangar")),
    "colony": (("dome", "pad"), ("dome", "dome", "pylon", "pylon", "antenna", "radar")),
}
# What a settlement's ground under a compound becomes.
SURFACES = {"city": Surface.PAVEMENT, "refinery": Surface.YARD, "farmland": Surface.FARMYARD}


def build(
    rng: random.Random, shape: Shape, step: float, knobs: Outposts, fluid: bool
) -> tuple[Shape, list[Prop], list[Rect]]:
    """Build the compounds: the ground levelled under them, their props, and where they are.

    Where they are: their lots (top, bottom, left, right). The shape's rows (`step` apart) loop; nothing crosses the
    loop's end.
    """
    rows, columns = shape.heights.shape
    loop, width = rows * step, (columns - 1) * step
    count = max(1, round(loop * width / knobs.spacing**2))
    sites: list[Rect] = []
    for _ in range(count):
        site = _site(rng, shape, step, knobs, fluid, sites)
        if site is not None:
            sites.append(site)
    heights, marks = shape.heights.copy(), None if shape.marks is None else shape.marks.copy()
    props: list[Prop] = []
    for site in sites:
        level = _level(shape.heights, site, step, fluid)
        weight = _weight(site, rows, columns, step)
        heights += (level - heights) * weight
        if marks is not None:
            marks *= 1 - weight
        props += _compound(rng, site, rng.choice(knobs.kinds))
    return Shape(heights, marks), props, sites


def clear(layout: Layout, sites: list[Rect], surface: Surface) -> Layout:
    """Make room for the compounds on a settlement: the ground under them repainted, what stood there gone."""
    painted = layout.surface.copy()
    for site in sites:
        top, bottom, left, right = (round(edge / SURFACE_STEP) for edge in shrink(site, -0.01))
        painted[max(top, 0) : bottom, max(left, 0) : right] = surface
    return replace(layout, surface=painted, props=outside(layout.props, sites))


def outside(props: list[Prop], sites: list[Rect]) -> list[Prop]:
    """Return the props not standing on any compound (nor right by it)."""
    return [prop for prop in props if not any(_overlaps(prop, site) for site in sites)]


def _overlaps(prop: Prop, site: Rect, margin: float = 0.01) -> bool:
    top, bottom, left, right = site
    return (
        prop.x + prop.width / 2 > left - margin
        and prop.x - prop.width / 2 < right + margin
        and prop.y + prop.length / 2 > top - margin
        and prop.y - prop.length / 2 < bottom + margin
    )


def _site(
    rng: random.Random, shape: Shape, step: float, knobs: Outposts, fluid: bool, taken: list[Rect]
) -> Rect | None:
    """Pick the flattest (and driest, most open) of a few places for a new compound, away from the others.

    None if none is free.
    """
    rows, columns = shape.heights.shape
    loop, width = rows * step, (columns - 1) * step
    best, best_score = None, math.inf
    for _ in range(TRIES):
        across = rng.uniform(*knobs.size)
        along = across * rng.uniform(0.7, 1.3)
        if across + 2 * BLEND > width or along + 2 * BLEND > loop:
            continue
        x = rng.uniform(across / 2 + BLEND, width - across / 2 - BLEND)
        y = rng.uniform(along / 2 + BLEND, loop - along / 2 - BLEND)
        site = (y - along / 2, y + along / 2, x - across / 2, x + across / 2)
        if any(_near(site, other) for other in taken):
            continue
        ground = _under(shape.heights, site, step)
        roughness = float(np.percentile(ground, 90) - np.percentile(ground, 10))
        dry = float(np.mean(ground > 0.002)) if fluid else 1.0
        covered = 0.0 if shape.marks is None else float(np.mean(_under(shape.marks, site, step)))
        score = roughness + 0.2 * (1 - dry) + 0.3 * covered  # flat, dry, in the open (a clearing, no reeds)
        if score < best_score:
            best, best_score = site, score
    return best


def _near(site: Rect, other: Rect) -> bool:
    top, bottom, left, right = site
    o_top, o_bottom, o_left, o_right = other
    gap = 2 * BLEND
    return left < o_right + gap and right > o_left - gap and top < o_bottom + gap and bottom > o_top - gap


def _under(heights: np.ndarray, site: Rect, step: float) -> np.ndarray:
    top, bottom, left, right = site
    rows = slice(int(top / step), math.ceil(bottom / step) + 1)
    columns = slice(int(left / step), math.ceil(right / step) + 1)
    return heights[rows, columns]


def _level(heights: np.ndarray, site: Rect, step: float, fluid: bool) -> float:
    level = float(np.percentile(_under(heights, site, step), LEVEL_AT))
    return max(level, DRY) if fluid else level


def _weight(site: Rect, rows: int, columns: int, step: float) -> np.ndarray:
    """1 on the compound, easing to 0 within BLEND around it."""
    top, bottom, left, right = site
    xs = np.arange(columns) * step
    ys = np.arange(rows) * step
    dx = np.maximum(np.maximum(left - xs, xs - right), 0.0)
    dy = np.maximum(np.maximum(top - ys, ys - bottom), 0.0)
    distance = np.hypot(dx[None, :], dy[:, None])
    return smoothstep(BLEND, 0.0, distance)


def _compound(rng: random.Random, site: Rect, kind: str) -> list[Prop]:
    """Build a compound: a building in each lot, the main ones first (in the biggest lots), then the others.

    Some compounds stand on an apron, packed; the others stand on the bare ground, looser, some lots left empty.
    """
    paved = rng.random() < PAVED_SHARE
    props = [_prop(rng, "apron", site, APRON_HEIGHT)] if paved else []
    main, others = COMPOUNDS[kind]
    cells = sorted(lots(rng, shrink(site, 0.012), SMALLEST_LOT), key=lambda cell: -_area(cell))
    for index, cell in enumerate(cells):
        if index < len(main):
            prop = main[index]
        elif not paved and rng.random() < EMPTY_LOTS:
            continue
        else:
            prop = rng.choice(others)
        props += _building(rng, prop, shrink(cell, 0.006 if paved else rng.uniform(0.008, 0.02)))
    return props


def _area(cell: Rect) -> float:
    top, bottom, left, right = cell
    return (bottom - top) * (right - left)


def _building(rng: random.Random, kind: str, cell: Rect) -> list[Prop]:
    """`kind` in its lot: long ones fill it, round ones stand in the middle (square), masts are thin."""
    top, bottom, left, right = cell
    y, x = (top + bottom) / 2, (left + right) / 2
    side = min(bottom - top, right - left)
    if kind == "pylon":
        return _pylons(rng, cell)
    if kind in ("hangar", "warehouse", "containers"):
        return [_prop(rng, kind, cell, _filling_height(rng, kind, side))]
    size, height = _standing(rng, kind, side)
    return [_prop(rng, kind, (y - size / 2, y + size / 2, x - size / 2, x + size / 2), height)]


def _filling_height(rng: random.Random, kind: str, side: float) -> float:
    if kind == "hangar":
        return min(side * rng.uniform(0.4, 0.55), 0.06)
    if kind == "warehouse":
        return rng.uniform(0.03, 0.055)
    return rng.choice((0.01, 0.02, 0.03))  # containers, one to three high


def _standing(rng: random.Random, kind: str, side: float) -> tuple[float, float]:
    """(size, height) of a round building or a mast, in a lot `side` across."""
    if kind == "tank":
        return side * 0.8, rng.uniform(0.04, 0.08)
    if kind == "stack":
        return 0.035, rng.uniform(0.15, 0.25)
    if kind == "radar":
        size = min(side * 0.85, 0.12)
        return size, size * rng.uniform(0.7, 1.0)
    if kind == "dome":
        size = min(side * 0.9, 0.14)
        return size, size * rng.uniform(0.35, 0.5)
    if kind == "pad":
        return min(side * 0.9, 0.12), 0.004
    return 0.03, rng.uniform(0.1, 0.18)  # an antenna


def _pylons(rng: random.Random, cell: Rect) -> list[Prop]:
    """Place a pair of pylons, along the lot."""
    top, bottom, left, right = cell
    y, x = (top + bottom) / 2, (left + right) / 2
    if right - left > bottom - top:
        spots = [(left + (right - left) * share, y) for share in (0.3, 0.7)]
    else:
        spots = [(x, top + (bottom - top) * share) for share in (0.3, 0.7)]
    height = rng.uniform(0.06, 0.1)
    return [_prop(rng, "pylon", (sy - 0.015, sy + 0.015, sx - 0.015, sx + 0.015), height) for sx, sy in spots]


def _prop(rng: random.Random, kind: str, rect: Rect, height: float) -> Prop:
    top, bottom, left, right = rect
    return Prop(
        kind, (left + right) / 2, (top + bottom) / 2, right - left, bottom - top, height, rng.randrange(1 << 30)
    )
