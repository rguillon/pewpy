"""Generate prop candidates: random assemblies of shapes, each with a fixed size and fixed colors.

    uv run python -m pewpy.tools.generate_props 20                    # 20 candidates in data/models/candidates/props/
    uv run python -m pewpy.tools.generate_props 20 --seed 7 --append  # 20 more, numbered after the ones there

A candidate is a prop description (see pewpy.scenery.ground.props.model) of kind "candidate", in a box about the size of
the game's props: a main body (a block, a tower, a hall, a vault, a silo, a dome), maybe stacked with setbacks, topped
(a parapet, roof units, fans, solar panels, a water tank, antennas and a dish, a helipad, a dome, a spire, a mast,
chimneys), with an annex beside it joined by pipes, and maybe a yard of barrels and crates around. Every body carries
its own details: floors of windows, pilasters and a cornice on a block; bands, ribs, a catwalk and a ladder on a tower;
buttresses, a ridge vent and a big door on a hall; ribs and a lit door on a vault; hoops on a silo or a dome; beacons on
tall things. To use one in the game, move it to data/models/props/ under a name of its own and set its kind.
"""

import argparse
import colorsys
import itertools
import json
import math
import random
from collections.abc import Callable
from typing import Any

from pewpy.data import SOURCE_DATA
from pewpy.scenery.ground.props.model import COLORS, PropModel
from pewpy.tools.common import batch

DEFAULT_OUT = SOURCE_DATA / "models" / "candidates" / "props"
KIND = "candidate"
LIGHTS = [(0.9, 0.1, 0.06), (0.25, 0.8, 0.95), (0.95, 0.6, 0.2), (0.6, 0.95, 0.4)]  # beacon, sci-fi, amber, green
WINDOW_LIGHTS = [(0.95, 0.75, 0.4), (0.6, 0.85, 1.0), (1.0, 0.9, 0.7)]
BEACON = (0.95, 0.12, 0.08)
ACCENTS = [(0.55, 0.42, 0.1), (0.45, 0.12, 0.08), (0.12, 0.3, 0.45), (0.5, 0.5, 0.48), (0.15, 0.35, 0.18)]
THIN = 0.0007  # how far trims stand out of a wall
FLOOR = (0.006, 0.009)  # a storey's height

Color = tuple[float, float, float]
Part = dict[str, Any]
Rect = tuple[float, float, float, float]  # x0, x1, y0, y1


class Palette:
    """A candidate's colors.

    Muted walls around one hue, a trim, a roof, a dark one for openings, glass, an accent (stripes, crates), a metal
    for the machinery, a bright light and its windows' light.
    """

    def __init__(self, rng: random.Random) -> None:
        hue = rng.random()
        saturation = rng.uniform(0.05, 0.35)
        value = rng.uniform(0.18, 0.42)
        self.walls = _hsv(hue, saturation, value)
        self.second = _hsv((hue + rng.uniform(-0.15, 0.15)) % 1, saturation * rng.uniform(0.5, 1.2), value * 0.85)
        self.trim = _shade(self.walls, rng.choice([0.75, 1.3]))
        self.roof = _hsv((hue + rng.choice([0.0, 0.5])) % 1, saturation * 0.6, value * rng.uniform(0.7, 1.25))
        self.dark = _hsv(hue, saturation, value * 0.35)
        self.glass = _hsv(rng.uniform(0.5, 0.65), 0.35, rng.uniform(0.08, 0.16))
        self.accent = rng.choice(ACCENTS)
        self.metal = _hsv(rng.uniform(0.55, 0.65), 0.05, rng.uniform(0.3, 0.45))
        self.light = rng.choice(LIGHTS)
        self.window = rng.choice(WINDOW_LIGHTS)


class Assembly:
    """A candidate being built: its box, its colors and its parts so far."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.width = rng.uniform(0.03, 0.16)
        self.length = rng.uniform(0.03, 0.16)
        self.height = rng.uniform(0.02, 0.06) if rng.random() < 0.6 else rng.uniform(0.06, 0.2)
        self.colors = Palette(rng)
        self.parts: list[Part] = []

    def chance(self, share: float) -> bool:
        """Whether a detail is there: true `share` of the time."""
        return self.rng.random() < share

    def add(self, shape: str, geometry: list[Any], **options: Any) -> None:  # noqa: ANN401 - colors, materials, numbers
        """Add a part: a shape of PropMesh, its geometry, its colors and options."""
        part: Part = {shape: _rounded(geometry)}
        for key, value in options.items():
            part[key] = [round(channel, 3) for channel in value] if key in COLORS else _rounded(value)
        self.parts.append(part)

    def box(self, rect: Rect, z0: float, z1: float, color: Color, **options: Any) -> None:  # noqa: ANN401 - see add
        """Add a box over a rect."""
        self.add("box", [*rect, z0, z1], color=color, **options)

    def light(self, x: float, y: float, z: float, size: float, color: Color | None = None) -> None:
        """Add a glowing cube sitting at (x, y, z)."""
        self.box(_around(x, y, size), z, z + size * 2, color or self.colors.light, material="LIGHT")

    def description(self) -> dict[str, Any]:
        """Return the candidate as a prop description."""
        size = _rounded([self.width, self.length, self.height])
        return {"kind": KIND, "size": size, "parts": self.parts}


# Bodies: (assembly, footprint, base, top) -> the rect its flat top offers to what stands on it, or None if it's
# closed (a pitched roof, a dome). Each adds its own details.
Body = Callable[[Assembly, Rect, float, float], Rect | None]


def block(a: Assembly, rect: Rect, base: float, top: float) -> Rect | None:
    """Build a box with floors of windows, pilasters, a cornice; a plinth if it stands on the ground."""
    colors = a.colors
    material = a.rng.choice(["PLAIN", "OFFICE", "HOMES", "PLAIN"])
    a.box(rect, base, top, colors.walls, material=material, top=colors.roof)
    if base == 0 and a.chance(0.6):
        a.box(_grown(rect, THIN * 1.5), 0, min(top, a.height * 0.06 + 0.002), colors.trim)
    floor = a.rng.uniform(*FLOOR)
    floors = int((top - base) / floor)
    if floors >= 1 and a.chance(0.85):
        style = a.rng.choice(["bands", "bands", "glass"])
        for level in range(floors):
            z = base + level * floor + floor * 0.35
            a.box(_grown(rect, THIN), z, z + floor * (0.4 if style == "bands" else 0.6), colors.glass)
        if style == "bands" and a.chance(0.7):
            _pilasters(a, rect, base, top)
        _lit_windows(a, rect, base, floor, floors)
    if a.chance(0.6):
        a.box(_grown(rect, THIN * 2), top - 0.0015, top, colors.trim)  # a cornice
    return rect


def tower(a: Assembly, rect: Rect, base: float, top: float) -> Rect | None:
    """Build an upright cylinder: bands, ribs, a catwalk with a railing, a ladder."""
    colors = a.colors
    x, y, radius = _middle(rect)
    height = top - base
    material = a.rng.choice(["METAL", "PLAIN", "OFFICE"])
    a.add("cylinder", [x, y, radius, base, top], color=colors.walls, material=material, top=colors.roof, segments=18)
    for _ in range(a.rng.randint(1, 3)):
        z = base + height * a.rng.uniform(0.15, 0.9)
        band = colors.light if a.chance(0.3) else colors.dark
        material = "LIGHT" if band == colors.light else "PLAIN"
        a.add("cylinder", [x, y, radius * 1.03, z, z + height * 0.03], color=band, material=material, segments=18)
    _tower_details(a, x, y, radius, base, top)
    inner = radius * 0.7
    return (x - inner, x + inner, y - inner, y + inner)


def hall(a: Assembly, rect: Rect, base: float, top: float) -> Rect | None:
    """Build walls and a pitched roof (gabled or gambrel): windows, buttresses, a ridge vent, a big door."""
    colors = a.colors
    x0, x1, y0, y1 = rect
    eaves = base + (top - base) * a.rng.uniform(0.45, 0.7)
    rise = top - eaves
    if a.chance(0.6):
        a.add("gabled", [*rect, base, eaves, top], walls=colors.walls, roof=colors.roof)
    else:
        a.box(rect, base, eaves, colors.walls, top=colors.walls)
        section = [[0, 0], [0.15, rise * 0.6], [0.5, rise], [0.85, rise * 0.6], [1, 0]]
        a.add("ridge_roof", [list(rect), eaves, section], walls=colors.walls, roof=colors.roof)
    along_x = (x1 - x0) >= (y1 - y0)
    if a.chance(0.7):  # a row of windows under the eaves, on the long walls
        z = base + (eaves - base) * 0.55
        a.box(_long_sides(rect, along_x, THIN, 0.08), z, z + (eaves - base) * 0.2, colors.glass)
    if a.chance(0.5):  # buttresses along the long walls
        count = max(2, int(max(x1 - x0, y1 - y0) / 0.02))
        for index in range(count + 1):
            share = 0.06 + 0.88 * index / count
            for side in (0, 1):
                a.box(_on_long_side(rect, along_x, share, side, 0.0015, 0.002), base, eaves * 0.85, colors.trim)
    if a.chance(0.6):  # a vent along the ridge
        middle = (y0 + y1) / 2 if along_x else (x0 + x1) / 2
        ridge = _span(rect, along_x, 0.2, middle - 0.0015, middle + 0.0015)
        a.box(ridge, top - 0.001, top + 0.0025, colors.metal, material="METAL")
    _end_door(a, rect, along_x, base, eaves * 0.8)
    if a.chance(0.4):  # a chimney through the roof
        x, y = a.rng.uniform(x0 + (x1 - x0) * 0.2, x1 - (x1 - x0) * 0.2), (y0 + y1) / 2
        x, y = (x, y) if along_x else (y, x)
        chimney = min(x1 - x0, y1 - y0) * 0.06
        a.add("cylinder", [x, y, chimney, eaves, top + rise * 0.4], color=colors.second, top=colors.dark, segments=8)
    return None


def vault(a: Assembly, rect: Rect, base: float, top: float) -> Rect | None:
    """Build low walls under a rounded roof (a hangar), ribbed, with a big door and a light over it."""
    colors = a.colors
    x0, x1, y0, y1 = rect
    eaves = base + (top - base) * a.rng.uniform(0.15, 0.4)
    a.box(rect, base, eaves, colors.walls, top=colors.walls)
    rise = top - eaves
    section = [(share, rise * math.sin(math.pi * share)) for share in (0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1)]
    a.add("ridge_roof", [list(rect), eaves, [list(point) for point in section]], walls=colors.walls,
          roof=colors.roof, material="METAL")  # fmt: skip
    along_x = (x1 - x0) >= (y1 - y0)
    start, end = (x0, x1) if along_x else (y0, y1)
    ribs = a.rng.randint(3, 7)
    for index in range(ribs):
        at = start + (end - start) * (index + 0.5) / ribs
        _arch(a, rect, along_x, at - 0.0008, at + 0.0008, eaves, section, 0.0008, colors.trim)
    _end_door(a, rect, along_x, base, eaves + rise * 0.6)
    return None


def silo(a: Assembly, rect: Rect, base: float, top: float) -> Rect | None:
    """Build a shape turned on a lathe (tapering, bulging or waisted), closed and hooped, a light on top."""
    colors = a.colors
    x, y, radius = _middle(rect)
    shape = a.rng.choice(["taper", "bulge", "waist"])
    factors = {"taper": (1, 0.85, 0.6, 0.4), "bulge": (0.8, 1, 0.95, 0.5), "waist": (1, 0.7, 0.75, 0.9)}[shape]
    shares = (0, 0.35, 0.75, 1)
    profile = [[base + (top - base) * share, radius * factor] for share, factor in zip(shares, factors, strict=True)]
    a.add("lathe", [x, y, profile], color=colors.walls, material="METAL", cap=colors.roof, segments=18)
    for share in sorted(a.rng.sample([0.12, 0.3, 0.5, 0.65, 0.85], a.rng.randint(1, 3))):
        z = base + (top - base) * share
        ring = _lerp(shares, factors, share) * radius * 1.03
        a.add("cylinder", [x, y, ring, z, z + (top - base) * 0.025], color=colors.dark, segments=18)
    top_radius = radius * factors[-1]
    if a.chance(0.6):
        a.add("lathe", [x, y, [[top, top_radius], [top + 0.002, top_radius]]], color=colors.metal, segments=18)
    if a.chance(0.5):
        a.light(x, y, top, max(top_radius * 0.12, 0.0008))
    inner = top_radius * 0.7
    return (x - inner, x + inner, y - inner, y + inner) if shape != "taper" else None


def dome(a: Assembly, rect: Rect, base: float, top: float) -> Rect | None:
    """Build a dome on a ring wall: hoops, a glowing band, an entrance, a light on top."""
    colors = a.colors
    x, y, radius = _middle(rect)
    wall = base + (top - base) * a.rng.uniform(0.0, 0.35)
    if wall > base:
        a.add("cylinder", [x, y, radius, base, wall], color=colors.second, top=colors.second, segments=20)
        if a.chance(0.6):
            z = base + (wall - base) * 0.6
            a.add("cylinder", [x, y, radius * 1.02, z, z + 0.0012], color=colors.light, material="LIGHT", segments=20)
    material = a.rng.choice(["METAL", "PLAIN"])
    height = top - wall
    a.add("ellipsoid", [x, y, wall, [radius, radius, height]], color=colors.walls, material=material, lower=0,
          segments=20, rings=8)  # fmt: skip
    if a.chance(0.6):  # hoops over the dome
        for share in (0.35, 0.65, 0.85)[: a.rng.randint(1, 3)]:
            ring = radius * math.sqrt(1 - share * share) * 1.01
            z = wall + height * share
            a.add("cylinder", [x, y, ring, z, z + 0.001], color=colors.trim, segments=20)
    door = radius * 0.25
    a.box((x - door, x + door, y + radius * 0.8, y + radius * 1.08), base, base + min(height, 0.012), colors.second,
          top=colors.second)  # fmt: skip
    if a.chance(0.6):
        a.light(x, y, top, max(radius * 0.04, 0.0008))
    return None


BODIES: list[Body] = [block, block, tower, hall, vault, silo, dome]
STACKABLE: list[Body] = [block, tower, silo]


# Tops: (assembly, the rect offered, its height) -> things standing on a flat roof.
Top = Callable[[Assembly, Rect, float], None]


def parapet(a: Assembly, rect: Rect, z: float) -> None:
    """Add a low wall round the roof's edge."""
    x0, x1, y0, y1 = rect
    t, h = 0.001, 0.002
    for side in ((x0, x1, y0, y0 + t), (x0, x1, y1 - t, y1), (x0, x0 + t, y0, y1), (x1 - t, x1, y0, y1)):
        a.box(side, z, z + h, a.colors.trim)


def roof_units(a: Assembly, rect: Rect, z: float) -> None:
    """Add boxes of machinery, some with a fan or a vent on top."""
    for _ in range(a.rng.randint(1, 4)):
        unit, top = _spot(a, rect, 0.12, 0.3), z + a.rng.uniform(0.002, 0.005)
        a.box(unit, z, top, a.colors.metal, material="METAL")
        if a.chance(0.5):
            x, y, radius = _middle(unit)
            a.add("disc", [x, y, radius * 0.7, top + 0.0002], color=a.colors.dark, segments=10)


def fans(a: Assembly, rect: Rect, z: float) -> None:
    """Add round cooling fans in a row."""
    x0, x1, y0, y1 = rect
    radius = min(x1 - x0, y1 - y0) * 0.1
    count = max(1, min(4, int((x1 - x0) / (radius * 2.6))))
    y = a.rng.uniform(y0 + radius * 1.3, y1 - radius * 1.3)
    for index in range(count):
        x = x0 + (x1 - x0) * (index + 0.5) / count
        a.add("cylinder", [x, y, radius, z, z + 0.002], color=a.colors.metal, top=a.colors.dark, segments=12)


def solar_panels(a: Assembly, rect: Rect, z: float) -> None:
    """Add rows of panels tilted to the sky."""
    x0, x1, y0, y1 = _grown(rect, -min(rect[1] - rect[0], rect[3] - rect[2]) * 0.1)
    rows = max(1, int((y1 - y0) / 0.008))
    depth = (y1 - y0) / rows
    for row in range(rows):
        low, high = y0 + row * depth, y0 + row * depth + depth * 0.75
        corners = [
            [x0, low, z + 0.0005],
            [x1, low, z + 0.0005],
            [x1, high, z + depth * 0.4],
            [x0, high, z + depth * 0.4],
        ]
        a.add("face", [corners], color=(0.06, 0.09, 0.18), material="METAL")


def water_tank(a: Assembly, rect: Rect, z: float) -> None:
    """Add a tank on four legs, with a pointed lid."""
    x, y, radius = _middle(_spot(a, rect, 0.3, 0.45))
    legs = z + radius * 1.5
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        a.box(_around(x + dx * radius * 0.6, y + dy * radius * 0.6, 0.0005), z, legs, a.colors.dark)
    a.add("cylinder", [x, y, radius, legs, legs + radius * 1.4], color=a.colors.second, segments=12)
    lid = [[legs + radius * 1.4, radius * 1.05], [legs + radius * 1.9, 0]]
    a.add("lathe", [x, y, lid], color=a.colors.roof, segments=12)


def antennas(a: Assembly, rect: Rect, z: float) -> None:
    """Add masts of different heights, lights on their tips, maybe a dish looking up."""
    for _ in range(a.rng.randint(1, 3)):
        x, y, _radius = _middle(_spot(a, rect, 0.05, 0.1))
        tip = z + a.height * a.rng.uniform(0.15, 0.5)
        a.box(_around(x, y, 0.0005), z, tip, a.colors.metal, material="METAL")
        if a.chance(0.6):
            a.light(x, y, tip, 0.0008, BEACON)
    if a.chance(0.6):
        x, y, radius = _middle(_spot(a, rect, 0.25, 0.4))
        a.add("cylinder", [x, y, radius * 0.15, z, z + radius * 0.5], color=a.colors.metal, segments=8)
        dish = [[z + radius * 0.5, radius * 0.1], [z + radius * 0.7, radius * 0.7], [z + radius * 0.8, radius]]
        a.add("lathe", [x, y, dish], color=(0.6, 0.6, 0.62), material="METAL", segments=14)


def helipad(a: Assembly, rect: Rect, z: float) -> None:
    """Add a landing pad: a dark disc, a painted ring, lights round it."""
    x, y, radius = _middle(rect)
    radius *= 0.8
    a.add("disc", [x, y, radius, z + 0.0003], color=a.colors.dark, segments=16)
    a.add("lathe", [x, y, [[z + 0.0004, radius * 0.7], [z + 0.0004, radius * 0.6]]], color=a.colors.accent,
          segments=16)  # fmt: skip
    for index in range(4):
        angle = math.pi / 4 + index * math.pi / 2
        a.light(x + math.cos(angle) * radius, y + math.sin(angle) * radius, z, 0.0006)


def skylights(a: Assembly, rect: Rect, z: float) -> None:
    """Add glazed strips on the roof."""
    x0, x1, y0, y1 = rect
    count = a.rng.randint(2, 4)
    for index in range(count):
        y = y0 + (y1 - y0) * (index + 0.5) / count
        strip = (x0 + (x1 - x0) * 0.15, x1 - (x1 - x0) * 0.15, y - (y1 - y0) * 0.06, y + (y1 - y0) * 0.06)
        lit = a.chance(0.3)
        a.box(strip, z, z + 0.0012, a.colors.window if lit else a.colors.glass, material="LIGHT" if lit else "PLAIN")


def lid(a: Assembly, rect: Rect, z: float) -> None:
    """Add a low dome."""
    x, y, radius = _middle(rect)
    a.add("ellipsoid", [x, y, z, [radius, radius, radius * 0.4]], color=a.colors.roof, material="METAL", lower=0)


def spire(a: Assembly, rect: Rect, z: float) -> None:
    """Add a stepped cone to a point, a light on its tip."""
    x, y, radius = _middle(rect)
    tip = z + a.height * a.rng.uniform(0.3, 0.7)
    step = z + (tip - z) * 0.3
    profile = [[z, radius * 0.8], [step, radius * 0.8], [step, radius * 0.5], [tip, 0]]
    a.add("lathe", [x, y, profile], color=a.colors.roof, material="METAL", segments=12)
    a.light(x, y, tip, radius * 0.08, BEACON)


def mast(a: Assembly, rect: Rect, z: float) -> None:
    """Add a lattice mast (four legs and crossbars), a light on its tip."""
    x, y, radius = _middle(rect)
    tip = z + a.height * a.rng.uniform(0.4, 1.0)
    half = max(radius * 0.12, 0.001)
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        a.box(_around(x + dx * half, y + dy * half, 0.0003), z, tip, a.colors.metal)
    bars = int((tip - z) / 0.006)
    for index in range(1, bars + 1):
        bar = z + (tip - z) * index / (bars + 1)
        a.box(_around(x, y, half + 0.0003), bar, bar + 0.0004, a.colors.metal)
    a.light(x, y, tip, half, BEACON)


def chimneys(a: Assembly, rect: Rect, z: float) -> None:
    """Add one to three chimneys, banded, dark at the mouth."""
    x0, x1, y0, y1 = rect
    radius = min(x1 - x0, y1 - y0) * a.rng.uniform(0.08, 0.15)
    for _ in range(a.rng.randint(1, 3)):
        x, y = a.rng.uniform(x0 + radius, x1 - radius), a.rng.uniform(y0 + radius, y1 - radius)
        top = z + a.height * a.rng.uniform(0.3, 0.8)
        a.add("cylinder", [x, y, radius, z, top], color=a.colors.second, top=a.colors.dark, segments=10)
        a.add("cylinder", [x, y, radius * 1.08, top - (top - z) * 0.12, top - (top - z) * 0.06], color=a.colors.accent,
              segments=10)  # fmt: skip


FLAT_TOPS: list[Top] = [roof_units, roof_units, fans, solar_panels, water_tank, antennas, helipad, skylights]
CROWNS: list[Top] = [lid, spire, mast, chimneys]  # the last thing on top: nothing stands on them


def annex(a: Assembly, rect: Rect) -> None:
    """Add a lower building beside the main one, with something on its roof."""
    height = a.height * a.rng.uniform(0.2, 0.5)
    body = a.rng.choice([block, block, hall, tower, dome])
    offered = body(a, rect, 0.0, height)
    if offered is not None and a.chance(0.6):
        a.rng.choice([roof_units, fans, antennas, parapet])(a, offered, height)


def pipes(a: Assembly, main: Rect, other: Rect) -> None:
    """Add pipes from the main body to the annex, low on their walls."""
    mx, my, _ = _middle(main)
    ox, oy, _ = _middle(other)
    across = abs(ox - mx) > abs(oy - my)
    for index in range(a.rng.randint(1, 3)):
        z = a.height * 0.06 + index * 0.0025
        offset = (index - 1) * 0.003
        if across:
            a.box((min(mx, ox), max(mx, ox), my + offset - 0.0006, my + offset + 0.0006), z, z + 0.0012, a.colors.metal,
                  material="METAL")  # fmt: skip
        else:
            a.box((mx + offset - 0.0006, mx + offset + 0.0006, min(my, oy), max(my, oy)), z, z + 0.0012, a.colors.metal,
                  material="METAL")  # fmt: skip


def yard(a: Assembly, outer: Rect, inner: Rect) -> None:
    """Add barrels, crates and small tanks, between the buildings and the box's edge."""
    for _ in range(a.rng.randint(3, 8)):
        for _attempt in range(20):
            x, y = a.rng.uniform(outer[0], outer[1]), a.rng.uniform(outer[2], outer[3])
            if not (inner[0] - 0.002 < x < inner[1] + 0.002 and inner[2] - 0.002 < y < inner[3] + 0.002):
                break
        else:
            continue
        room = min(x - outer[0], outer[1] - x, y - outer[2], outer[3] - y)
        size = min(room, a.rng.uniform(0.0015, 0.004))
        if size < 0.0008:
            continue
        what = a.rng.choice(["barrels", "crate", "crate", "tank"])
        if what == "barrels":
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1))[: a.rng.randint(1, 4)]:
                bx, by = x + (dx - 0.5) * size, y + (dy - 0.5) * size
                a.add("cylinder", [bx, by, size * 0.45, 0, size * 1.2], color=a.colors.accent, segments=8)
        elif what == "crate":
            stacked = a.rng.randint(1, 2)
            for level in range(stacked):
                a.box(_around(x, y, size), level * size * 2, (level + 1) * size * 2 - 0.0002, a.colors.accent)
        else:
            a.add("cylinder", [x, y, size, 0, size * 1.5], color=a.colors.metal, material="METAL", segments=10)
            a.add("ellipsoid", [x, y, size * 1.5, [size, size, size * 0.4]], color=a.colors.metal, lower=0)


def candidate(rng: random.Random) -> dict[str, Any]:
    """Return a random prop description."""
    a = Assembly(rng)
    outer = (-a.width / 2, a.width / 2, -a.length / 2, a.length / 2)
    built = outer
    if a.chance(0.4):  # a yard all round
        built = _grown(outer, -min(a.width, a.length) * rng.uniform(0.1, 0.2))
    main, annexes = _split(a, built)
    body = rng.choice(BODIES)
    top = a.height if a.chance(0.7) else a.height * rng.uniform(0.4, 0.7)
    offered, top = _stack(a, body, main, top)
    if offered is not None:
        _roof(a, body, offered, top)
    if offered is not None and top > 0.08 and a.chance(0.7):  # beacons on the corners of tall things
        x0, x1, y0, y1 = offered
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            a.light(x, y, top, 0.0008, BEACON)
    if body is block and a.chance(0.7):
        _door(a, main, top)
    for rect in annexes:
        annex(a, rect)
        if a.chance(0.6):
            pipes(a, main, rect)
    if built != outer:
        yard(a, outer, built)
    return a.description()


def _split(a: Assembly, built: Rect) -> tuple[Rect, list[Rect]]:
    """Return where the main body stands and where its annexes do: half the time, an annex takes a side."""
    if not a.chance(0.5):
        return built, []
    x0, x1, y0, y1 = built
    width, length = x1 - x0, y1 - y0
    share = a.rng.uniform(0.55, 0.75)
    if width >= length:
        cut = x0 + width * share
        return (x0, cut, y0, y1), [(cut + 0.002, x1, y0 + length * 0.15, y1 - length * 0.15)]
    cut = y1 - length * share  # the annex behind: the door faces down the screen
    return (x0, x1, cut, y1), [(x0 + width * 0.15, x1 - width * 0.15, y0, cut - 0.002)]


def _stack(a: Assembly, body: Body, main: Rect, top: float) -> tuple[Rect | None, float]:
    """Build the main body, maybe with setbacks on it; return its flat top (if any) and its height."""
    offered = body(a, main, 0.0, top)
    for _ in range(a.rng.choice([0, 0, 1, 2]) if body in STACKABLE else 0):
        if offered is None:
            break
        x0, x1, y0, y1 = offered
        inset = a.rng.uniform(0.12, 0.25)
        dx, dy = (x1 - x0) * inset, (y1 - y0) * inset
        upper = top + a.height * a.rng.uniform(0.3, 0.8)
        offered = a.rng.choice(STACKABLE)(a, (x0 + dx, x1 - dx, y0 + dy, y1 - dy), top, upper)
        top = upper
    return offered, top


def _roof(a: Assembly, body: Body, rect: Rect, z: float) -> None:
    """Fill a flat roof: a parapet, a couple of things on it, maybe a crown."""
    if body is block and a.chance(0.6):
        parapet(a, rect, z)
    for flat in a.rng.sample(FLAT_TOPS, a.rng.randint(0, 2)):
        flat(a, rect, z)
    if a.chance(0.5):
        a.rng.choice(CROWNS)(a, rect, z)


def _tower_details(a: Assembly, x: float, y: float, radius: float, base: float, top: float) -> None:
    """Add a tower's ribs, catwalk with its railing, and ladder (each maybe)."""
    colors = a.colors
    height = top - base
    if a.chance(0.5):  # ribs up the side
        count = a.rng.choice([4, 6, 8])
        for index in range(count):
            angle = 2 * math.pi * index / count
            rx, ry = x + math.cos(angle) * radius, y + math.sin(angle) * radius
            a.box(_around(rx, ry, radius * 0.06), base, top, colors.trim)
    if a.chance(0.5):  # a catwalk with a railing
        z = base + height * a.rng.uniform(0.6, 0.95)
        a.add("cylinder", [x, y, radius * 1.15, z, z + 0.0008], color=colors.metal, segments=18)
        railing = [[z + 0.0008, radius * 1.15], [z + 0.0025, radius * 1.15]]
        a.add("lathe", [x, y, railing], color=colors.metal, material="METAL", segments=18)
    if a.chance(0.5):  # a ladder
        a.box((x - 0.0008, x + 0.0008, y + radius, y + radius + 0.0008), base, top, colors.metal)


def _pilasters(a: Assembly, rect: Rect, base: float, top: float) -> None:
    """Add upright strips on the walls, over the window bands: at the corners and evenly between."""
    x0, x1, y0, y1 = rect
    t = THIN * 1.6
    spacing = a.rng.uniform(0.008, 0.016)
    for start, end, fixed, along_x in (
        (x0, x1, y0, True),
        (x0, x1, y1, True),
        (y0, y1, x0, False),
        (y0, y1, x1, False),
    ):
        count = max(1, round((end - start) / spacing))
        for index in range(count + 1):
            at = start + (end - start) * index / count
            if along_x:
                a.box((at - 0.0006, at + 0.0006, fixed - t, fixed + t), base, top, a.colors.trim)
            else:
                a.box((fixed - t, fixed + t, at - 0.0006, at + 0.0006), base, top, a.colors.trim)


def _lit_windows(a: Assembly, rect: Rect, base: float, floor: float, floors: int) -> None:
    """Light a few windows, glowing on the window bands."""
    x0, x1, y0, y1 = rect
    for _ in range(a.rng.randint(0, min(10, floors * 2))):
        z = base + a.rng.randrange(floors) * floor + floor * 0.38
        size = floor * 0.17
        side = a.rng.randrange(4)
        if side < 2:
            x = a.rng.uniform(x0 + size * 2, x1 - size * 2)
            y = y0 - THIN * 1.3 if side == 0 else y1 + THIN * 1.3
            window = (x - size * 1.5, x + size * 1.5, y - THIN * 0.3, y + THIN * 0.3)
        else:
            y = a.rng.uniform(y0 + size * 2, y1 - size * 2)
            x = x0 - THIN * 1.3 if side == 2 else x1 + THIN * 1.3
            window = (x - THIN * 0.3, x + THIN * 0.3, y - size * 1.5, y + size * 1.5)
        a.box(window, z, z + size * 2, a.colors.window, material="LIGHT")


def _door(a: Assembly, rect: Rect, top: float) -> None:
    """Add a dark door on the wall facing down the screen, a canopy and a light over it."""
    x0, x1, _y0, y1 = rect
    width = min((x1 - x0) * a.rng.uniform(0.12, 0.3), 0.012)
    x = a.rng.uniform(x0 + width, x1 - width)
    height = min(top * 0.6, a.rng.uniform(0.004, 0.007))
    a.box((x - width / 2, x + width / 2, y1, y1 + 0.0012), 0, height, a.colors.dark)
    if a.chance(0.6):
        a.box((x - width * 0.7, x + width * 0.7, y1, y1 + 0.003), height, height + 0.0008, a.colors.accent)
    if a.chance(0.5):
        a.light(x, y1 + 0.0012, height + 0.001, 0.0006)


def _end_door(a: Assembly, rect: Rect, along_x: bool, base: float, top: float) -> None:
    """Add a big door on an end wall, with a light over it."""
    x0, x1, y0, y1 = rect
    across = (y1 - y0) if along_x else (x1 - x0)
    half = across * a.rng.uniform(0.2, 0.35)
    if along_x:
        middle = (y0 + y1) / 2
        a.box((x1, x1 + 0.0012, middle - half, middle + half), base, top, a.colors.dark)
        a.light(x1 + 0.001, middle, top + 0.001, 0.0008)
    else:
        middle = (x0 + x1) / 2
        a.box((middle - half, middle + half, y1, y1 + 0.0012), base, top, a.colors.dark)
        a.light(middle, y1 + 0.001, top + 0.001, 0.0008)


def _arch(
    a: Assembly,
    rect: Rect,
    along_x: bool,
    start: float,
    end: float,
    eaves: float,
    section: list[tuple[float, float]],
    out: float,
    color: Color,
) -> None:
    """Add a rib over a vault, from `start` to `end` along it: the roof's cross-section, standing `out` off it."""
    x0, x1, y0, y1 = rect
    low, high = (y0, y1) if along_x else (x0, x1)
    low, high = low - out, high + out
    points = [
        (low + (high - low) * share, eaves + rise + out * (0.0 if share in (0, 1) else 1.0)) for share, rise in section
    ]

    def point(along: float, across: float, z: float) -> list[float]:
        return [along, across, z] if along_x else [across, along, z]

    for (pa, za), (pb, zb) in itertools.pairwise(points):
        corners = [point(start, pa, za), point(end, pa, za), point(end, pb, zb), point(start, pb, zb)]
        a.add("face", [corners], color=color, material="METAL")


def _long_sides(rect: Rect, along_x: bool, out: float, inset: float) -> Rect:
    """Return a rect over the whole footprint, standing `out` off its long walls, `inset` short of its ends."""
    x0, x1, y0, y1 = rect
    if along_x:
        d = (x1 - x0) * inset
        return (x0 + d, x1 - d, y0 - out, y1 + out)
    d = (y1 - y0) * inset
    return (x0 - out, x1 + out, y0 + d, y1 - d)


def _on_long_side(rect: Rect, along_x: bool, share: float, side: int, wide: float, deep: float) -> Rect:
    """Return a small rect on a long wall (`side` 0 or 1), `share` of the way along it, `wide` along and `deep` out."""
    x0, x1, y0, y1 = rect
    if along_x:
        x = x0 + (x1 - x0) * share
        y = y0 - deep / 2 if side == 0 else y1 + deep / 2
        return (x - wide / 2, x + wide / 2, y - deep / 2, y + deep / 2)
    y = y0 + (y1 - y0) * share
    x = x0 - deep / 2 if side == 0 else x1 + deep / 2
    return (x - deep / 2, x + deep / 2, y - wide / 2, y + wide / 2)


def _span(rect: Rect, along_x: bool, inset: float, low: float, high: float) -> Rect:
    """Return a rect along the footprint's length (`inset` short of its ends), from `low` to `high` across."""
    x0, x1, y0, y1 = rect
    if along_x:
        d = (x1 - x0) * inset
        return (x0 + d, x1 - d, low, high)
    d = (y1 - y0) * inset
    return (low, high, y0 + d, y1 - d)


def _spot(a: Assembly, rect: Rect, smallest: float, biggest: float) -> Rect:
    """Return a random rect inside `rect`, its sides a share of rect's."""
    x0, x1, y0, y1 = rect
    wide, long = (x1 - x0) * a.rng.uniform(smallest, biggest), (y1 - y0) * a.rng.uniform(smallest, biggest)
    x, y = a.rng.uniform(x0 + wide / 2, x1 - wide / 2), a.rng.uniform(y0 + long / 2, y1 - long / 2)
    return (x - wide / 2, x + wide / 2, y - long / 2, y + long / 2)


def _middle(rect: Rect) -> tuple[float, float, float]:
    """Return the middle of a rect and the radius of the biggest circle in it."""
    x0, x1, y0, y1 = rect
    return (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) / 2


def _around(x: float, y: float, half: float) -> Rect:
    return (x - half, x + half, y - half, y + half)


def _grown(rect: Rect, by: float) -> Rect:
    x0, x1, y0, y1 = rect
    return (x0 - by, x1 + by, y0 - by, y1 + by)


def _lerp(shares: tuple[float, ...], values: tuple[float, ...], at: float) -> float:
    """Return the value at `at` on the broken line through (shares, values)."""
    for (s0, v0), (s1, v1) in itertools.pairwise(zip(shares, values, strict=True)):
        if s0 <= at <= s1:
            return v0 + (v1 - v0) * (at - s0) / (s1 - s0)
    return values[-1]


def _shade(color: Color, factor: float) -> Color:
    return (min(color[0] * factor, 1.0), min(color[1] * factor, 1.0), min(color[2] * factor, 1.0))


def _hsv(hue: float, saturation: float, value: float) -> Color:
    return colorsys.hsv_to_rgb(hue, min(saturation, 1.0), min(value, 1.0))


def _rounded(value: Any) -> Any:  # noqa: ANN401 - a JSON value of any shape
    if isinstance(value, list | tuple):
        return [_rounded(item) for item in value]
    if isinstance(value, float):
        return round(value, 5)
    return value


def to_json(description: dict[str, Any]) -> str:
    """Return the description as JSON, a part on each line."""
    parts = ",\n".join(f"    {json.dumps(part)}" for part in description["parts"])
    head = f'  "kind": {json.dumps(description["kind"])},\n  "size": {json.dumps(description["size"])},\n'
    return "{\n" + head + '  "parts": [\n' + parts + "\n  ]\n}\n"


def main() -> None:
    """Generate the candidates the command line asks for and write them."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("count", type=int, help="how many to write")
    batch.options(parser, DEFAULT_OUT, "data/models/candidates/props/")
    args = parser.parse_args()
    seed, first = batch.start(args)
    rng = random.Random(seed)
    for number in range(first, first + args.count):
        description = candidate(rng)
        PropModel(f"{number:03d}", description)  # it builds: no missing or unknown argument
        (args.out / f"{number:03d}.json").write_text(to_json(description))
    batch.report("prop candidates", args.count, first, args.out, seed)


if __name__ == "__main__":
    main()
