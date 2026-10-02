"""Farm silos: a tall cylinder with a dome or a cone on top, banded; sometimes two side by side."""

import random

from pewpy.scenery.ground.props.mesh import METAL, PropMesh, radius, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    color = varied(rng, c.silo, 0.1)
    if rng.random() < 0.25 and prop.width > prop.length * 0.9:  # a pair, thinner
        r = radius(prop) * 0.55
        for dx in (-r * 0.95, r * 0.95):
            _silo(mesh, rng, prop.x + dx, prop.y, r, prop.base, prop.base + prop.height * rng.uniform(0.85, 1.0), color)
        return
    _silo(mesh, rng, prop.x, prop.y, radius(prop), prop.base, prop.base + prop.height, color)


def _silo(
    mesh: PropMesh,
    rng: random.Random,
    x: float,
    y: float,
    r: float,
    z0: float,
    top: float,
    color: tuple[float, float, float],
) -> None:
    mesh.cylinder(x, y, r, z0, top, color, METAL)
    for band in range(1, 4):  # darker rings around it
        z = z0 + (top - z0) * band / 4
        mesh.cylinder(x, y, r * 1.04, z, z + 0.002, shade(color, 0.7), METAL, segments=14)
    if rng.random() < 0.6:
        mesh.ellipsoid(x, y, top, (r, r, r * 0.7), color, METAL, lower=0.0)
    else:
        mesh.lathe(x, y, [(top, r * 1.05), (top + r * 0.9, r * 0.12)], shade(color, 0.85), METAL)
