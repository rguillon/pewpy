"""Radar stations: a dish looking up on a pedestal, with a feed spike and a red light; or a white radome ball on a
short tower.
"""

import random

from pewpy.scenery.ground.props.mesh import LIGHT, METAL, PLAIN, PropMesh, radius, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    r, z0, height = radius(prop), prop.base, prop.height
    hull = varied(rng, rng.choice(c.hull), 0.05)
    x, y = prop.x, prop.y
    if rng.random() < 0.6:  # a dish
        mount = z0 + height * 0.45
        mesh.cylinder(x, y, r * 0.22, z0, mount, shade(hull, 0.7), METAL, segments=10)
        mesh.lathe(x, y, [(mount, r * 0.15), (mount + height * 0.1, r * 0.6), (mount + height * 0.22, r)], hull, METAL)
        mesh.disc(x, y, r * 0.97, mount + height * 0.19, shade(hull, 0.85), PLAIN)  # the dish's face
        spike = z0 + height - 0.004
        mesh.box(x - 0.0015, x + 0.0015, y - 0.0015, y + 0.0015, mount, spike, c.roof_unit, METAL)
        mesh.box(x - 0.003, x + 0.003, y - 0.003, y + 0.003, spike, spike + 0.004, c.beacon, LIGHT)
        return
    ball = min(r, height * 0.35)  # a radome on a tower
    middle = z0 + height - ball
    mesh.lathe(x, y, [(z0, r * 0.45), (middle, r * 0.3)], shade(hull, 0.6), METAL, segments=6)
    mesh.ellipsoid(x, y, middle, (ball, ball, ball), shade(hull, 1.25), PLAIN, segments=16, rings=8)
