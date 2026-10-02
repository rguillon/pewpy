"""Hangars: a long vaulted hall (a rounded roof straight from the ground, or on low walls).

A big dark door at one end with a light over it; sometimes two halls side by side.
"""

import math
import random

from pewpy.scenery.ground.props.mesh import LIGHT, METAL, PLAIN, PropMesh, footprint, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors

ARCH = (0.0, 0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.92, 1.0)  # shares across the roof


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build a hangar."""
    x0, x1, y0, y1 = footprint(prop)
    walls = varied(rng, rng.choice(c.hangar_walls))
    along_x = (x1 - x0) >= (y1 - y0)
    if rng.random() < 0.3 and min(x1 - x0, y1 - y0) > 0.05:  # two halls side by side, a gap between
        if along_x:
            middle = (y0 + y1) / 2
            halls = [(x0, x1, y0, middle - 0.003), (x0, x1, middle + 0.003, y1)]
        else:
            middle = (x0 + x1) / 2
            halls = [(x0, middle - 0.003, y0, y1), (middle + 0.003, x1, y0, y1)]
    else:
        halls = [(x0, x1, y0, y1)]
    on_walls = rng.random() < 0.5
    door_end = rng.random() < 0.5
    for hall in halls:
        _hall(mesh, hall, prop.base, prop.height, walls, on_walls, door_end, c)


def _hall(
    mesh: PropMesh,
    hall: tuple[float, float, float, float],
    z0: float,
    height: float,
    walls: tuple[float, float, float],
    on_walls: bool,
    door_end: bool,
    c: PropColors,
) -> None:
    x0, x1, y0, y1 = hall
    eaves = z0 + height * 0.3 if on_walls else z0 + 0.001
    mesh.box(x0, x1, y0, y1, z0, eaves, walls, PLAIN, top=walls)
    rise = z0 + height - eaves
    section = [(share, rise * math.sqrt(max(0.0, 1 - (2 * share - 1) ** 2))) for share in ARCH]
    mesh.ridge_roof(hall, eaves, section, walls, shade(walls, 1.15), METAL)
    # The door: a dark opening on one end, most of the way across and up; a light over it.
    along_x = (x1 - x0) >= (y1 - y0)
    across = (y1 - y0) if along_x else (x1 - x0)
    middle = (y0 + y1) / 2 if along_x else (x0 + x1) / 2
    door_top = z0 + height * (0.75 if on_walls else 0.6)
    half = across * 0.33
    if along_x:
        end = x1 if door_end else x0
        out = 0.0015 if door_end else -0.0015
        mesh.box(min(end, end + out), max(end, end + out), middle - half, middle + half, z0, door_top, c.vent, PLAIN)
        mesh.box(
            min(end, end + 2 * out),
            max(end, end + 2 * out),
            middle - 0.002,
            middle + 0.002,
            door_top + 0.002,
            door_top + 0.005,
            c.scifi_light,
            LIGHT,
        )
    else:
        end = y1 if door_end else y0
        out = 0.0015 if door_end else -0.0015
        mesh.box(middle - half, middle + half, min(end, end + out), max(end, end + out), z0, door_top, c.vent, PLAIN)
        mesh.box(
            middle - 0.002,
            middle + 0.002,
            min(end, end + 2 * out),
            max(end, end + 2 * out),
            door_top + 0.002,
            door_top + 0.005,
            c.scifi_light,
            LIGHT,
        )
