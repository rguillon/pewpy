"""Antenna masts: a tall square lattice tower narrowing to the top, a few dishes or crossbars on it.

And a red light at the tip.
"""

import random

from pewpy.scenery.ground.props.mesh import LIGHT, METAL, PLAIN, PropMesh, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build an antenna mast."""
    x, y, z0 = prop.x, prop.y, prop.base
    top = z0 + prop.height
    foot = min(prop.width, prop.length, 0.03) / 2
    steel = varied(rng, shade(c.roof_unit, 0.8), 0.05)
    mesh.lathe(x, y, [(z0, foot), (top, foot * 0.2)], steel, METAL, segments=4)
    for _ in range(rng.randint(1, 3)):  # crossbars or small dishes up the mast
        z = z0 + prop.height * rng.uniform(0.4, 0.85)
        reach = foot * (1 - (z - z0) / prop.height) + 0.004
        if rng.random() < 0.5:
            mesh.box(x - reach * 1.6, x + reach * 1.6, y - 0.001, y + 0.001, z, z + 0.002, steel, PLAIN)
        else:
            mesh.ellipsoid(x + reach, y, z, (0.002, 0.005, 0.005), shade(steel, 1.3), METAL, segments=8, rings=3)
    mesh.box(x - 0.003, x + 0.003, y - 0.003, y + 0.003, top, top + 0.005, c.beacon, LIGHT)
