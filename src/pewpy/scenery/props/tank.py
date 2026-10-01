"""Refinery tanks: domed, floating-roof (a flat lid low inside a rim), or a sphere on legs."""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import METAL, PLAIN, PropMesh, radius, shade, varied
from pewpy.scenery.settlement import Prop


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    r, top = radius(prop), prop.base + prop.height
    metal = varied(rng, rng.choice(c.refinery_metals))
    roll = rng.random()
    if roll < 0.2 and prop.height > r:  # a sphere on legs
        middle = prop.base + prop.height * 0.55
        size = min(r, (top - prop.base) * 0.45)
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            lx, ly = prop.x + dx * size * 0.6, prop.y + dy * size * 0.6
            mesh.box(lx - 0.002, lx + 0.002, ly - 0.002, ly + 0.002, prop.base, middle, shade(metal, 0.7), PLAIN)
        mesh.ellipsoid(prop.x, prop.y, middle, (size, size, size), metal, METAL, segments=16, rings=8)
        return
    mesh.cylinder(prop.x, prop.y, r, prop.base, top, metal, METAL, segments=20)
    mesh.cylinder(
        prop.x,
        prop.y,
        r * 1.02,
        top - (top - prop.base) * 0.15,
        top - (top - prop.base) * 0.13,
        shade(metal, 0.75),
        METAL,
        segments=20,
    )
    if roll < 0.55:  # a dome
        lid = shade(metal, 1.15)
        mesh.ellipsoid(prop.x, prop.y, top, (r, r, r * 0.12), lid, METAL, lower=0.0, segments=20, rings=3)
    else:  # a floating roof: a lid sunk inside the rim
        mesh.disc(prop.x, prop.y, r * 0.95, top - 0.004, shade(metal, 0.6), PLAIN, segments=20)
        mesh.lathe(prop.x, prop.y, [(top - 0.004, r * 0.95), (top, r * 0.95)], shade(metal, 0.8), METAL, segments=20)
    if rng.random() < 0.5:  # a stair winding up the side, a darker band
        mesh.cylinder(prop.x, prop.y, r * 1.03, prop.base, prop.base + 0.003, shade(metal, 0.6), PLAIN, segments=20)
