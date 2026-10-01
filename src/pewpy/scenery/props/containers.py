"""Stacks of shipping containers in rows, one to three high, in a few colors; some spaces empty."""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import METAL, PropMesh, footprint, shade, varied
from pewpy.scenery.settlement import Prop

LONG, WIDE, HIGH = 0.024, 0.01, 0.01  # one container, world units
GAP = 0.002


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    along_x = (x1 - x0) >= (y1 - y0)
    length, across = ((x1 - x0), (y1 - y0)) if along_x else ((y1 - y0), (x1 - x0))
    slots = max(1, int(length / (LONG + GAP)))
    rows = max(1, int(across / (WIDE + GAP)))
    levels = max(1, round(prop.height / HIGH))
    for row in range(rows):
        if rows > 2 and row % 3 == 2:  # an aisle every two rows
            continue
        for slot in range(slots):
            stack = rng.randint(0, levels)
            for level in range(stack):
                a = slot * (LONG + GAP)
                b = row * (WIDE + GAP)
                z = prop.base + level * HIGH
                color = varied(rng, rng.choice(c.containers), 0.06)
                if along_x:
                    box = (x0 + a, x0 + a + LONG, y0 + b, y0 + b + WIDE)
                else:
                    box = (x0 + b, x0 + b + WIDE, y0 + a, y0 + a + LONG)
                mesh.box(*box, z, z + HIGH * 0.95, color, METAL, top=shade(color, 1.1))
