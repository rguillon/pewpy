"""Energy pylons: a six-sided spire narrowing to the top, glowing rings around it and a glowing crystal at the tip."""

import random

from pewpy.scenery.ground.props.mesh import LIGHT, METAL, PropMesh, shade, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build a pylon: a tapering metal mast topped with a glowing crystal."""
    x, y, z0 = prop.x, prop.y, prop.base
    foot = min(prop.width, prop.length, 0.03) / 2
    hull = varied(rng, shade(rng.choice(c.hull), 0.7), 0.05)
    crystal = foot * 0.6
    top = z0 + prop.height - crystal * 2
    mesh.lathe(x, y, [(z0, foot), (z0 + (top - z0) * 0.15, foot * 0.7), (top, foot * 0.35)], hull, METAL, segments=6)
    for share in sorted(rng.uniform(0.3, 0.85) for _ in range(rng.randint(1, 3))):
        z = z0 + (top - z0) * share
        ring = foot * (0.7 - 0.35 * share) + 0.0015
        mesh.lathe(x, y, [(z, ring), (z + 0.002, ring)], c.scifi_light, LIGHT, segments=6)
    # The crystal: two pyramids point to point, glowing.
    mesh.lathe(
        x,
        y,
        [(top, 0.0001), (top + crystal, crystal * 0.6), (top + crystal * 2, 0.0001)],
        c.scifi_light,
        LIGHT,
        segments=4,
    )
