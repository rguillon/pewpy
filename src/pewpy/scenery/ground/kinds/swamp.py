"""A swamp: murky water full of muddy islets with reeds, and dead trees on them."""

import random

import numpy as np

from pewpy.scenery.ground.landscapes import Flora, Generator, Landscape, inside, level_for_share, noise, scatter
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import Knobs


class Swamp(Landscape):
    knobs = ("water_share", "size", "detail_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Murky water full of low muddy islets with reeds (and dead trees, see `DeadTrees`). Marks: reeds."""
        value = 0.7 * noise(rng, rows, columns, knobs["size"], step)
        value += 0.3 * noise(rng, rows, columns, knobs["detail_size"], step)
        sea = level_for_share(value, knobs["water_share"])
        heights = np.where(value > sea, 0.003 + (value - sea) * 0.12, (value - sea) * 0.3)
        reeds = smoothstep(sea + 0.03, sea + 0.07, value) * smoothstep(0.45, 0.6, noise(rng, rows, columns, 0.12, step))
        return Shape(heights, reeds)


class DeadTrees(Flora):
    knobs = ("chance", "size", "height")

    def props(self, rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
        """A few dead trees on the swamp's islets (on a share `chance` of their points)."""
        rows = shape.heights.shape[0]
        size = knobs["size"]
        return [
            Prop("dead_tree", x, y, size, size, rng.uniform(*knobs["height"]), rng.randrange(1 << 30))
            for x, y in scatter(rng, shape.heights > 0.006, knobs["chance"], step_x, step_y)
            if inside(y, 0.02, rows, step_y)
        ]
