"""Dead trees in the swamp: a bare grey trunk with a few broken branches.

Sometimes forked at the top or snapped short.
"""

import random

from pewpy.scenery.ground.props.mesh import PLAIN, PropMesh, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build a dead tree."""
    x, y, z0 = prop.x, prop.y, prop.base
    height = prop.height * (rng.uniform(0.45, 0.6) if rng.random() < 0.2 else 1.0)  # some snapped short
    wood = varied(rng, c.dead_wood, 0.12)
    mesh.box(x - 0.002, x + 0.002, y - 0.002, y + 0.002, z0, z0 + height, wood, PLAIN)
    for _ in range(rng.randint(1, 4)):
        z = z0 + height * rng.uniform(0.4, 0.85)
        length = rng.uniform(0.008, 0.018) * rng.choice((-1, 1))
        if rng.random() < 0.5:
            mesh.box(min(x, x + length), max(x, x + length), y - 0.0012, y + 0.0012, z, z + 0.0025, wood, PLAIN)
        else:
            mesh.box(x - 0.0012, x + 0.0012, min(y, y + length), max(y, y + length), z, z + 0.0025, wood, PLAIN)
    if rng.random() < 0.4:  # forked at the top
        top = z0 + height
        for dx in (-0.004, 0.004):
            mesh.box(x + dx - 0.0012, x + dx + 0.0012, y - 0.0012, y + 0.0012, top - 0.004, top + 0.01, wood, PLAIN)
