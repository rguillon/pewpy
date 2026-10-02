"""Hedges around fields: a row of bushes of slightly different heights and greens, with the odd gap."""

import random

from pewpy.scenery.ground.props.mesh import FOLIAGE, PropMesh, footprint, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    along_x = (x1 - x0) >= (y1 - y0)
    length = (x1 - x0) if along_x else (y1 - y0)
    pieces = max(1, round(length / 0.04))
    step = length / pieces
    for index in range(pieces):
        if pieces > 2 and rng.random() < 0.08:  # a gap
            continue
        a, b = index * step, (index + 1) * step
        height = prop.height * rng.uniform(0.8, 1.2)
        green = varied(rng, c.hedge, 0.15)
        if along_x:
            mesh.box(x0 + a, x0 + b, y0, y1, prop.base, prop.base + height, green, FOLIAGE)
        else:
            mesh.box(x0, x1, y0 + a, y0 + b, prop.base, prop.base + height, green, FOLIAGE)
