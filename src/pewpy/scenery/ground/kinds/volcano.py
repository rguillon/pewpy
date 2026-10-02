"""Volcanic ground: black hills, lakes and rivers of lava."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, noise, normalized
from pewpy.scenery.ground.relief import Shape, eroded_noise, smoothstep
from pewpy.scenery.params import Knobs


class Volcano(Landscape):
    """Volcanic hills with lakes and rivers of lava."""

    knobs = ("size", "lava_level", "river_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape black volcanic hills with lakes and rivers of lava in the low ground.

        Lakes below `lava_level` (0 to 1 of the noise), rivers below 0.
        """
        value = normalized(eroded_noise(rng, rows, columns, knobs["size"] / step, octaves=6))
        level = knobs["lava_level"]
        heights = np.where(
            value > level, (np.maximum(value - level, 0.0) / (1 - level)) ** 1.4 * max_height, (value - level) * 0.2
        )
        # Rivers: channels carved along a line of the noise, with sloping banks (not a wall a grid point wide).
        channel = smoothstep(0.04, 0.015, np.abs(noise(rng, rows, columns, knobs["river_size"], step) - 0.5))
        return Shape(heights * (1 - channel) - 0.008 * channel)
