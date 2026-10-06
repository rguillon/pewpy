"""Badlands: bare ridges eroded into branching gullies, striped in layers (painted like the canyon)."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, normalized
from pewpy.scenery.ground.relief import Shape, ridged_mountains, smoothstep
from pewpy.scenery.params import Knobs


class Badlands(Landscape):
    """Eroded ridges and gullies."""

    knobs = ("size", "floor")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape sharp ridges branching into gullies, about `size` apart; below `floor` (0 to 1), flat sandy floors.

        Marks: 0.5 the floors' sand.
        """
        value = normalized(ridged_mountains(rng, rows, columns, knobs["size"] / step, octaves=6))
        floor = knobs["floor"]
        rise = np.clip((value - floor) / (1 - floor), 0.0, 1.0) ** 1.3
        heights = 0.004 + max_height * rise
        return Shape(heights, np.where(smoothstep(0.02, 0.0, rise) > 0.5, 0.5, 0.0))
