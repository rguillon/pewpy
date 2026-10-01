"""Trees: round broadleaf crowns, pointed conifers, or a bushy cluster of small crowns. Seen from above, the crown
is all that shows: few sides, there can be hundreds on screen.
"""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import FOLIAGE, PropMesh, shade, varied
from pewpy.scenery.settlement import Prop


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    green = varied(rng, rng.choice(c.trees), 0.12)
    roll = rng.random()
    if roll < 0.25:  # a conifer: a dark cone
        r = min(prop.width, prop.length) / 2 * 0.8
        z0, top = prop.base + prop.height * 0.1, prop.base + prop.height * 1.3
        mesh.lathe(
            prop.x,
            prop.y,
            [(z0, r), (z0 + (top - z0) * 0.45, r * 0.6), (top, 0.0)],
            shade(green, 0.75),
            FOLIAGE,
            segments=7,
        )
        return
    if roll < 0.4 and prop.width > 0.025:  # a cluster of three small crowns
        for index in range(3):
            dx, dy = rng.uniform(-0.25, 0.25) * prop.width, rng.uniform(-0.25, 0.25) * prop.length
            size = rng.uniform(0.5, 0.65)
            crown = (prop.width / 2 * size, prop.length / 2 * size, prop.height * 0.35)
            z = prop.base + prop.height * (0.45 + 0.1 * index)
            mesh.ellipsoid(
                prop.x + dx, prop.y + dy, z, crown, varied(rng, green, 0.08), FOLIAGE, lower=-0.5, segments=6, rings=3
            )
        return
    crown = (prop.width / 2, prop.length / 2, prop.height * 0.45)
    middle = prop.base + prop.height * 0.55
    mesh.ellipsoid(prop.x, prop.y, middle, crown, green, FOLIAGE, lower=-0.5, segments=7, rings=3)
