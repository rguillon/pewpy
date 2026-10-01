"""City buildings: low blocks, mid-rises, towers. Each picks its walls, roof and a style for its height."""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import FOLIAGE, HOMES, LIGHT, METAL, OFFICE, PLAIN, ROOFING, PropMesh, footprint, varied
from pewpy.scenery.settlement import Prop

TOWER = 0.25  # taller than this: a tower
MIDRISE = 0.12


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    z0, height = prop.base, prop.height
    walls = varied(rng, rng.choice(c.building_walls))
    roof = rng.choice(c.roofs)
    material = OFFICE if height > MIDRISE or rng.random() < 0.5 else HOMES
    narrow = min(x1 - x0, y1 - y0)
    if height > TOWER and narrow > 0.07:
        top = _tower(mesh, rng, (x0, x1, y0, y1), z0, height, walls, roof, material, c)
    elif height > MIDRISE and rng.random() < 0.4:
        top = _stepped(mesh, rng, (x0, x1, y0, y1), z0, height, walls, roof, material)
    else:
        mesh.box(x0, x1, y0, y1, z0, z0 + height, walls, material, top=roof, top_material=ROOFING)
        top = (x0, x1, y0, y1, z0 + height)
    _roof(mesh, rng, top, c)


def _tower(
    mesh: PropMesh,
    rng: random.Random,
    footprint_: tuple[float, float, float, float],
    z0: float,
    height: float,
    walls: tuple[float, float, float],
    roof: tuple[float, float, float],
    material: int,
    c: PropColors,
) -> tuple[float, float, float, float, float]:
    """A setback tower (one or two narrower tiers), maybe crowned with a mast; a red light on a corner."""
    x0, x1, y0, y1 = footprint_
    top = z0 + height
    floor = z0
    for share in sorted(rng.uniform(0.45, 0.75) for _ in range(rng.choice((1, 1, 2)))):  # one or two setbacks
        waist = z0 + height * share
        mesh.box(x0, x1, y0, y1, floor, waist, walls, material, top=roof, top_material=ROOFING)
        inset = min(x1 - x0, y1 - y0) * rng.uniform(0.1, 0.2)
        x0, x1, y0, y1 = x0 + inset, x1 - inset, y0 + inset, y1 - inset
        floor = waist
    mesh.box(x0, x1, y0, y1, floor, top, walls, material, top=roof, top_material=ROOFING)
    if rng.random() < 0.35:  # a mast with a light at its tip
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        mast = rng.uniform(0.04, 0.08)
        mesh.box(mx - 0.002, mx + 0.002, my - 0.002, my + 0.002, top, top + mast, c.roof_unit, METAL)
        mesh.box(mx - 0.004, mx + 0.004, my - 0.004, my + 0.004, top + mast, top + mast + 0.006, c.beacon, LIGHT)
    else:
        mesh.box(x0, x0 + 0.006, y0, y0 + 0.006, top, top + 0.006, c.beacon, LIGHT)
    return (x0, x1, y0, y1, top)


def _stepped(
    mesh: PropMesh,
    rng: random.Random,
    footprint_: tuple[float, float, float, float],
    z0: float,
    height: float,
    walls: tuple[float, float, float],
    roof: tuple[float, float, float],
    material: int,
) -> tuple[float, float, float, float, float]:
    """A mid-rise on a wider, lower podium along one side."""
    x0, x1, y0, y1 = footprint_
    podium = z0 + height * rng.uniform(0.25, 0.45)
    mesh.box(x0, x1, y0, y1, z0, podium, walls, material, top=roof, top_material=ROOFING)
    cut = rng.uniform(0.3, 0.5)  # the share of the podium left low, on one side
    first_side = rng.random() < 0.5
    if x1 - x0 > y1 - y0:
        x0, x1 = (x0 + (x1 - x0) * cut, x1) if first_side else (x0, x1 - (x1 - x0) * cut)
    else:
        y0, y1 = (y0 + (y1 - y0) * cut, y1) if first_side else (y0, y1 - (y1 - y0) * cut)
    mesh.box(x0, x1, y0, y1, podium, z0 + height, walls, material, top=roof, top_material=ROOFING)
    return (x0, x1, y0, y1, z0 + height)


def _roof(mesh: PropMesh, rng: random.Random, top: tuple[float, float, float, float, float], c: PropColors) -> None:
    """What's on the roof: machinery, a water tank on legs, a garden, or nothing."""
    x0, x1, y0, y1, z = top
    if x1 - x0 < 0.03 or y1 - y0 < 0.03:
        return
    roll = rng.random()
    if roll < 0.06:  # a roof garden: a few planters, a path between them
        across = (x1 - x0) >= (y1 - y0)
        count = rng.randint(2, 3)
        for index in range(count):
            a, b = index / count + 0.06, (index + 1) / count - 0.06
            px0, px1 = (x0 + (x1 - x0) * a, x0 + (x1 - x0) * b) if across else (x0 + 0.006, x1 - 0.006)
            py0, py1 = (y0 + 0.006, y1 - 0.006) if across else (y0 + (y1 - y0) * a, y0 + (y1 - y0) * b)
            green = varied(rng, rng.choice(c.trees), 0.15)
            mesh.box(px0, px1, py0, py1, z, z + 0.004, green, FOLIAGE)
        return
    if roll < 0.2:  # a water tank on legs
        r = min(x1 - x0, y1 - y0) * 0.18
        cx, cy = rng.uniform(x0 + r * 1.5, x1 - r * 1.5), rng.uniform(y0 + r * 1.5, y1 - r * 1.5)
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            lx, ly = cx + dx * r * 0.6, cy + dy * r * 0.6
            mesh.box(lx - 0.0012, lx + 0.0012, ly - 0.0012, ly + 0.0012, z, z + 0.012, c.roof_unit, PLAIN)
        mesh.lathe(cx, cy, [(z + 0.012, r), (z + 0.028, r), (z + 0.034, r * 0.3)], c.roof_unit, METAL, segments=10)
        return
    for _ in range(rng.randint(0, 3)):  # machinery
        size = rng.uniform(0.008, 0.018)
        if x1 - x0 > 2 * size and y1 - y0 > 2 * size:
            cx, cy = rng.uniform(x0 + size, x1 - size), rng.uniform(y0 + size, y1 - size)
            mesh.box(cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2, z, z + size * 0.6, c.roof_unit, PLAIN)
