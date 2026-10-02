"""Palms: a thin trunk, leaning a little, and a star of five to eight drooping fronds."""

import math
import random

from pewpy.scenery.ground.props.mesh import FOLIAGE, PLAIN, PropMesh, varied
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x, y, z0, height, reach = prop.x, prop.y, prop.base, prop.height, prop.width / 2
    lean = rng.uniform(0, 2 * math.pi)
    tilt = rng.uniform(0.0, 0.25) * height
    tx, ty = x + math.cos(lean) * tilt, y + math.sin(lean) * tilt  # the top of the trunk
    top = z0 + height
    trunk = varied(rng, c.palm_trunk)
    for step in range(3):  # the trunk in three segments, so it leans smoothly
        a, b = step / 3, (step + 1) / 3
        ax, ay = x + (tx - x) * a, y + (ty - y) * a
        bx, by = x + (tx - x) * b, y + (ty - y) * b
        mesh.box(
            min(ax, bx) - 0.0015,
            max(ax, bx) + 0.0015,
            min(ay, by) - 0.0015,
            max(ay, by) + 0.0015,
            z0 + height * a,
            z0 + height * b,
            trunk,
            PLAIN,
        )
    fronds = varied(rng, c.palm_fronds, 0.12)
    count = rng.randint(5, 8)
    turn = rng.uniform(0, 2 * math.pi)
    for index in range(count):
        angle = turn + index * 2 * math.pi / count + rng.uniform(-0.2, 0.2)
        along = (math.cos(angle), math.sin(angle))
        side = (-along[1] * 0.006, along[0] * 0.006)
        length = reach * rng.uniform(0.75, 1.1)
        tip = (tx + along[0] * length, ty + along[1] * length, top - height * rng.uniform(0.15, 0.35))
        corners = [(tx - side[0], ty - side[1], top), (tx + side[0], ty + side[1], top), tip, tip]
        norm = math.hypot(0.3, 1.0)  # tilted outwards a little, like the drooping frond
        mesh.quad(corners, (along[0] * 0.3 / norm, along[1] * 0.3 / norm, 1.0 / norm), fronds, FOLIAGE)
