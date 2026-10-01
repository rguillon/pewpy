"""Sci-fi domes: a habitat on a ring wall with a glowing band, a light on top, sometimes an airlock tube out to
one side; or a glass dome full of plants.
"""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import FOLIAGE, LIGHT, METAL, PLAIN, PropMesh, radius, shade, varied
from pewpy.scenery.settlement import Prop


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    r, z0, height = radius(prop) * 0.85, prop.base, prop.height
    x, y = prop.x, prop.y
    hull = varied(rng, rng.choice(c.hull), 0.05)
    wall = z0 + height * 0.18
    mesh.cylinder(x, y, r, z0, wall, shade(hull, 0.75), METAL, segments=20)
    mesh.cylinder(x, y, r * 1.01, wall - height * 0.08, wall - height * 0.05, c.scifi_light, LIGHT, segments=20)
    if rng.random() < 0.3:  # a glass dome with plants in it
        mesh.ellipsoid(x, y, wall, (r * 0.8, r * 0.8, height * 0.5), varied(rng, c.trees[0], 0.2), FOLIAGE, lower=0.0)
        mesh.ellipsoid(x, y, wall, (r, r, height * 0.82), varied(rng, c.glasshouse, 0.05), METAL, lower=0.0, rings=5)
    else:
        mesh.ellipsoid(x, y, wall, (r, r, height * 0.82), hull, METAL, lower=0.0, segments=20, rings=6)
        mesh.cylinder(x, y, r * 0.12, z0 + height - 0.002, z0 + height + 0.002, c.scifi_light, LIGHT, segments=8)
    if rng.random() < 0.5:  # an airlock tube out to the edge of its lot
        side = rng.choice((-1.0, 1.0))
        reach, half = radius(prop), r * 0.18
        if rng.random() < 0.5:
            mesh.box(
                min(x + side * r * 0.8, x + side * reach),
                max(x + side * r * 0.8, x + side * reach),
                y - half,
                y + half,
                z0,
                z0 + half * 2,
                shade(hull, 0.9),
                PLAIN,
            )
        else:
            mesh.box(
                x - half,
                x + half,
                min(y + side * r * 0.8, y + side * reach),
                max(y + side * r * 0.8, y + side * reach),
                z0,
                z0 + half * 2,
                shade(hull, 0.9),
                PLAIN,
            )
