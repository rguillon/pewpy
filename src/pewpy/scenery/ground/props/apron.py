"""Aprons: the concrete slab a compound stands on (grounds/outposts.py), in panels, with painted lines along it."""

import random

from pewpy.scenery.ground.props.mesh import PLAIN, ROOFING, PropMesh, footprint, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build a concrete apron, with painted lines along it."""
    x0, x1, y0, y1 = footprint(prop)
    top = prop.base + prop.height
    concrete = varied(rng, c.apron, 0.04)
    mesh.box(x0, x1, y0, y1, prop.base, top, concrete, PLAIN, top=concrete, top_material=ROOFING)
    along_x = (x1 - x0) >= (y1 - y0)
    for share in (0.2, 0.8) if rng.random() < 0.6 else (0.5,):  # painted lines along the slab
        if along_x:
            line = y0 + (y1 - y0) * share
            mesh.box(x0 + 0.01, x1 - 0.01, line - 0.0008, line + 0.0008, top, top + 0.0004, c.marking, PLAIN)
        else:
            line = x0 + (x1 - x0) * share
            mesh.box(line - 0.0008, line + 0.0008, y0 + 0.01, y1 - 0.01, top, top + 0.0004, c.marking, PLAIN)
