"""Greenhouses: long low halls of pale glass on a short wall, or rounded polytunnels, in rows on the farms."""

import math
import random

from pewpy.scenery.ground.props.mesh import METAL, PLAIN, PropMesh, footprint, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    wall = prop.base + prop.height * 0.35
    glass = varied(rng, c.glasshouse, 0.05)
    if rng.random() < 0.5:
        mesh.gabled(x0, x1, y0, y1, prop.base, wall, prop.base + prop.height, glass, glass, METAL)
    else:  # a polytunnel: a rounded roof straight from the ground
        wall = prop.base + 0.002
        mesh.box(x0, x1, y0, y1, prop.base, wall, glass, METAL, top=glass)
        rise = prop.height
        section = [(share, rise * math.sin(math.pi * share)) for share in (0.0, 0.12, 0.3, 0.5, 0.7, 0.88, 1.0)]
        mesh.ridge_roof((x0, x1, y0, y1), wall, section, glass, glass, METAL)
    # The frame: thin ribs across the roof.
    along_x = (x1 - x0) >= (y1 - y0)
    length = (x1 - x0) if along_x else (y1 - y0)
    for index in range(1, int(length / 0.015)):
        at = (x0 if along_x else y0) + index * 0.015
        if along_x:
            mesh.box(at, at + 0.0012, y0, y1, prop.base, wall + 0.001, c.pipe, PLAIN)
        else:
            mesh.box(x0, x1, at, at + 0.0012, prop.base, wall + 0.001, c.pipe, PLAIN)
