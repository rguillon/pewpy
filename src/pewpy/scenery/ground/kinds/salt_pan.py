"""A salt pan: a flat white crust cracked into plates (painted by the shader), with pools of brine."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, level_for_share, noise
from pewpy.scenery.ground.relief import Shape
from pewpy.scenery.params import Knobs


class SaltPan(Landscape):
    """A flat cracked crust with pools."""

    knobs = ("size", "pool_share")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape a nearly flat crust, swelling a little, with pools of brine (`pool_share` of it) in the hollows.

        Marks: how far from a pool (0 at its shore, 1 well away), for the crust's colors.
        """
        value = 0.7 * noise(rng, rows, columns, knobs["size"], step) + 0.3 * noise(rng, rows, columns, 0.15, step)
        shore = level_for_share(value, 1 - knobs["pool_share"])
        heights = np.where(value > shore, 0.002 + (value - shore) * 0.04 * max_height / 0.1, (value - shore) * 0.08)
        return Shape(heights, np.clip((value - shore) / 0.15, 0.0, 1.0))
