"""Industrial halls: a long building with a sawtooth roof (glazed north lights), or a flat roof with vents; loading
doors along one side, sometimes an office block with windows at one end.
"""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import METAL, OFFICE, PLAIN, ROOFING, PropMesh, footprint, varied
from pewpy.scenery.settlement import Prop

Rect = tuple[float, float, float, float]  # x0, x1, y0, y1
TOOTH = 0.022  # a sawtooth roof's teeth, about this far apart


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    z0, top = prop.base, prop.base + prop.height
    walls = varied(rng, c.plant_walls)
    roof = varied(rng, c.plant_roof)
    along_x = (x1 - x0) >= (y1 - y0)
    if rng.random() < 0.3:  # an office block at one end, a bit taller, with windows
        length = (x1 - x0) if along_x else (y1 - y0)
        cut = length * rng.uniform(0.2, 0.3)
        first = rng.random() < 0.5
        if along_x:
            office = (x0, x0 + cut, y0, y1) if first else (x1 - cut, x1, y0, y1)
            x0, x1 = (x0 + cut, x1) if first else (x0, x1 - cut)
        else:
            office = (x0, x1, y0, y0 + cut) if first else (x0, x1, y1 - cut, y1)
            y0, y1 = (y0 + cut, y1) if first else (y0, y1 - cut)
        office_walls = varied(rng, rng.choice(c.building_walls))
        office_top = z0 + prop.height * rng.uniform(1.1, 1.35)
        mesh.box(*office, z0, office_top, office_walls, OFFICE, top=roof, top_material=ROOFING)
    hall = (x0, x1, y0, y1)
    if rng.random() < 0.5:
        _sawtooth(mesh, hall, z0, top, walls, roof, along_x, c)
    else:
        mesh.box(x0, x1, y0, y1, z0, top, walls, PLAIN, top=roof, top_material=ROOFING)
        for _ in range(rng.randint(1, 4)):  # roof vents
            r = rng.uniform(0.003, 0.006)
            if x1 - x0 > 4 * r and y1 - y0 > 4 * r:
                vx, vy = rng.uniform(x0 + 2 * r, x1 - 2 * r), rng.uniform(y0 + 2 * r, y1 - 2 * r)
                mesh.cylinder(vx, vy, r, top, top + r * 1.2, c.roof_unit, METAL, segments=8)
    _doors(mesh, rng, hall, z0, prop.height, along_x, c)


def _sawtooth(
    mesh: PropMesh,
    hall: Rect,
    z0: float,
    top: float,
    walls: tuple[float, float, float],
    roof: tuple[float, float, float],
    along_x: bool,
    c: PropColors,
) -> None:
    """Walls up to the eaves, then teeth along the hall: each a roof sloping up, then a steep glazed face down."""
    x0, x1, y0, y1 = hall
    eaves = z0 + (top - z0) * 0.7
    mesh.box(x0, x1, y0, y1, z0, eaves, walls, PLAIN, top=roof)
    start, end = (x0, x1) if along_x else (y0, y1)
    teeth = max(2, round((end - start) / TOOTH))
    for index in range(teeth):
        a = start + (end - start) * index / teeth
        b = start + (end - start) * (index + 1) / teeth
        # A narrow strip across the hall: its ridge runs across, its section goes along the hall.
        tooth = (a, b, y0, y1) if along_x else (x0, x1, a, b)
        mesh.ridge_roof(tooth, eaves, [(0.0, 0.0), (0.85, top - eaves), (1.0, 0.0)], walls, roof, METAL)
        glass = a + (b - a) * 0.86
        if along_x:
            mesh.box(glass, glass + 0.0008, y0, y1, eaves, top - 0.001, c.glass, PLAIN)
        else:
            mesh.box(x0, x1, glass, glass + 0.0008, eaves, top - 0.001, c.glass, PLAIN)


def _doors(
    mesh: PropMesh, rng: random.Random, hall: Rect, z0: float, height: float, along_x: bool, c: PropColors
) -> None:
    """Loading doors along one long side: dark, a little proud of the wall."""
    x0, x1, y0, y1 = hall
    start, end = (x0, x1) if along_x else (y0, y1)
    count = max(1, min(5, int((end - start) / 0.03)))
    side = rng.random() < 0.5
    door_top = z0 + min(height * 0.7, 0.02)
    for index in range(count):
        middle = start + (end - start) * (index + 0.5) / count
        half = min(0.007, (end - start) / count * 0.35)
        if along_x:
            wall = y1 if side else y0
            mesh.box(middle - half, middle + half, wall - 0.0012, wall + 0.0012, z0, door_top, c.vent, PLAIN)
        else:
            wall = x1 if side else x0
            mesh.box(wall - 0.0012, wall + 0.0012, middle - half, middle + half, z0, door_top, c.vent, PLAIN)
