"""Cooling towers: the refinery's big concrete hyperboloids, open at the top, a dark inside."""

import random

from pewpy.scenery.ground.props.mesh import PLAIN, PropMesh, radius, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    r, z0, height = radius(prop), prop.base, prop.height
    waist = rng.uniform(0.6, 0.72)  # how narrow it gets, as a share of its base
    profile = [
        (z0, r),
        (z0 + height * 0.35, r * (waist + (1 - waist) * 0.3)),
        (z0 + height * 0.7, r * waist),
        (z0 + height, r * (waist + 0.08)),
    ]
    concrete = varied(rng, c.concrete, 0.06)
    mesh.lathe(prop.x, prop.y, profile, concrete, PLAIN, segments=18)
    mesh.disc(prop.x, prop.y, r * (waist + 0.06), z0 + height - 0.01, c.vent, PLAIN, segments=18)  # the dark inside
    mesh.lathe(
        prop.x,
        prop.y,
        [(z0 + height * 0.86, r * (waist + 0.04)), (z0 + height * 0.9, r * (waist + 0.05))],
        shade(concrete, 0.8),
        PLAIN,
        segments=18,
    )
