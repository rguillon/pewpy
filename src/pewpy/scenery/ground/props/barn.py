"""Barns: long and red, a gabled or a gambrel (two-pitch) roof, a big door at one end."""

import random

from pewpy.scenery.ground.props.mesh import PLAIN, PropMesh, footprint, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build a barn."""
    x0, x1, y0, y1 = footprint(prop)
    eaves, ridge = prop.base + prop.height * 0.55, prop.base + prop.height
    walls, roof = varied(rng, c.barn_walls), varied(rng, c.barn_roof)
    if rng.random() < 0.5:
        mesh.gabled(x0, x1, y0, y1, prop.base, eaves, ridge, walls, roof, PLAIN)
    else:
        mesh.box(x0, x1, y0, y1, prop.base, eaves, walls, PLAIN, top=walls)
        _gambrel(mesh, (x0, x1, y0, y1), eaves, ridge, walls, roof)
    # The door: a darker panel on one end wall.
    door = shade(walls, 0.55)
    if (x1 - x0) >= (y1 - y0):
        mid = (y0 + y1) / 2
        mesh.box(
            x0 - 0.002, x0, mid - 0.006, mid + 0.006, prop.base, prop.base + (eaves - prop.base) * 0.8, door, PLAIN
        )
    else:
        mid = (x0 + x1) / 2
        mesh.box(
            mid - 0.006, mid + 0.006, y0 - 0.002, y0, prop.base, prop.base + (eaves - prop.base) * 0.8, door, PLAIN
        )


def _gambrel(
    mesh: PropMesh,
    footprint_: tuple[float, float, float, float],
    eaves: float,
    ridge: float,
    walls: tuple[float, float, float],
    roof: tuple[float, float, float],
) -> None:
    """Two pitches on each side: steep from the eaves, then gentle to the ridge."""
    rise = ridge - eaves
    section = [(0.0, 0.0), (0.15, rise * 0.6), (0.5, rise), (0.85, rise * 0.6), (1.0, 0.0)]
    mesh.ridge_roof(footprint_, eaves, section, walls, roof)
