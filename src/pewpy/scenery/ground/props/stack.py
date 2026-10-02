"""Stacks: a tall flare with its flame, or a chimney banded red and white; one or two."""

import random

from pewpy.scenery.ground.props.mesh import LIGHT, PLAIN, PropMesh, radius, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    r, top = radius(prop), prop.base + prop.height
    if rng.random() < 0.35:  # a pair of banded chimneys
        for dx in (-r * 0.45, r * 0.45):
            _banded(mesh, prop.x + dx, prop.y, r * 0.4, prop.base, prop.base + prop.height * rng.uniform(0.8, 1.0), c)
        return
    if rng.random() < 0.4:
        _banded(mesh, prop.x, prop.y, r * 0.6, prop.base, top, c)
        return
    mesh.cylinder(prop.x, prop.y, r * 0.6, prop.base, top, varied(rng, c.stack), PLAIN, segments=12)
    flame = (r * 0.8, r * 0.8, r * rng.uniform(1.3, 2.0))
    mesh.ellipsoid(prop.x, prop.y, top + flame[2] * 0.45, flame, c.flame, LIGHT, segments=8, rings=4)


def _banded(mesh: PropMesh, x: float, y: float, r: float, z0: float, top: float, c: PropColors) -> None:
    """A chimney tapering a little, with bands of the beacon's red near the top, and a light at its rim."""
    mesh.lathe(x, y, [(z0, r * 1.15), (top, r * 0.85)], c.stack, PLAIN, segments=12, cap=c.vent)
    for band in range(2):
        z = top - (band + 1) * (top - z0) * 0.12
        mesh.lathe(x, y, [(z, r * 0.92), (z + (top - z0) * 0.05, r * 0.9)], c.beacon, PLAIN, segments=12)
    mesh.box(x - 0.002, x + 0.002, y + r * 0.85 - 0.002, y + r * 0.85 + 0.002, top, top + 0.004, c.beacon, LIGHT)
