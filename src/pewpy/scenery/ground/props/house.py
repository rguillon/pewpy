"""Farmhouses: walls up to the eaves, a gabled or a hipped roof, maybe a chimney."""

import random

from pewpy.scenery.ground.props.mesh import HOMES, PLAIN, PropMesh, footprint, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    eaves, ridge = prop.base + prop.height * rng.uniform(0.55, 0.65), prop.base + prop.height
    walls, roof = varied(rng, c.house_walls), varied(rng, rng.choice(c.house_roofs))
    if rng.random() < 0.6:
        mesh.gabled(x0, x1, y0, y1, prop.base, eaves, ridge, walls, roof, HOMES)
    else:
        mesh.box(x0, x1, y0, y1, prop.base, eaves, walls, HOMES, top=walls)
        hipped(mesh, (x0, x1, y0, y1), eaves, ridge, roof)
    if rng.random() < 0.6:  # a chimney through the roof
        cx = rng.uniform(x0 + 0.006, x1 - 0.006)
        cy = rng.uniform(y0 + 0.006, y1 - 0.006)
        mesh.box(cx - 0.003, cx + 0.003, cy - 0.003, cy + 0.003, eaves, ridge + 0.006, c.stack, PLAIN)


def hipped(
    mesh: PropMesh,
    footprint_: tuple[float, float, float, float],
    eaves: float,
    ridge: float,
    roof: tuple[float, float, float],
) -> None:
    """A roof sloping down on all four sides from a short ridge along the longer side."""
    x0, x1, y0, y1 = footprint_
    if (x1 - x0) >= (y1 - y0):
        half, middle = (y1 - y0) / 2, (y0 + y1) / 2
        a, b = (x0 + half, middle, ridge), (x1 - half, middle, ridge)
        faces = [
            [(x0, y0, eaves), (x1, y0, eaves), b, a],
            [(x1, y0, eaves), (x1, y1, eaves), b],
            [(x1, y1, eaves), (x0, y1, eaves), a, b],
            [(x0, y1, eaves), (x0, y0, eaves), a],
        ]
    else:
        half, middle = (x1 - x0) / 2, (x0 + x1) / 2
        a, b = (middle, y0 + half, ridge), (middle, y1 - half, ridge)
        faces = [
            [(x0, y0, eaves), (x1, y0, eaves), a],
            [(x1, y0, eaves), (x1, y1, eaves), b, a],
            [(x1, y1, eaves), (x0, y1, eaves), b],
            [(x0, y1, eaves), (x0, y0, eaves), a, b],
        ]
    for corners in faces:
        mesh.face(corners, roof, PLAIN)
