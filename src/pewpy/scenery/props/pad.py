"""Landing pads: an eight-sided platform with a painted ring and cross, lights around it, and sometimes a small
craft parked on it.
"""

import math
import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import LIGHT, METAL, PLAIN, PropMesh, radius, shade, varied
from pewpy.scenery.settlement import Prop


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    r, x, y = radius(prop) * 0.95, prop.x, prop.y
    deck = prop.base + max(prop.height, 0.003)
    mesh.cylinder(x, y, r, prop.base, deck, varied(rng, c.apron, 0.04), PLAIN, segments=8)
    mesh.disc(x, y, r * 0.8, deck + 0.0004, c.marking, PLAIN, segments=24)
    mesh.disc(x, y, r * 0.72, deck + 0.0008, shade(c.apron, 0.85), PLAIN, segments=24)
    bar, arm = r * 0.07, r * 0.45
    mesh.box(x - arm, x + arm, y - bar, y + bar, deck, deck + 0.0012, c.marking, PLAIN)
    mesh.box(x - bar, x + bar, y - arm, y + arm, deck, deck + 0.0012, c.marking, PLAIN)
    for index in range(8):  # lights around the edge
        angle = 2 * math.pi * (index + 0.5) / 8
        lx, ly = x + r * 0.9 * math.cos(angle), y + r * 0.9 * math.sin(angle)
        mesh.box(lx - 0.0015, lx + 0.0015, ly - 0.0015, ly + 0.0015, deck, deck + 0.002, c.scifi_light, LIGHT)
    if rng.random() < 0.45:  # a small craft: a flat body, swept wings, a lit cockpit
        hull = varied(rng, rng.choice(c.hull), 0.06)
        length = r * 0.7
        mesh.ellipsoid(x, y, deck + 0.004, (length * 0.28, length, 0.004), hull, METAL, segments=10, rings=4)
        mesh.face(
            [
                (x, y - length * 0.2, deck + 0.004),
                (x - length * 0.8, y + length * 0.6, deck + 0.003),
                (x + length * 0.8, y + length * 0.6, deck + 0.003),
            ],
            shade(hull, 0.8),
            METAL,
        )
        mesh.box(
            x - 0.002, x + 0.002, y - length * 0.75, y - length * 0.45, deck + 0.006, deck + 0.008, c.scifi_light, LIGHT
        )
