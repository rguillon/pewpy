"""A forest: a canopy over rolling ground, clearings, a winding river."""

import numpy as np

from pewpy.scenery.landscapes import Generator, Landscape, meander, noise
from pewpy.scenery.params import Knobs
from pewpy.scenery.relief import Shape, smoothstep


class Forest(Landscape):
    knobs = ("canopy_size", "river_spacing", "river_width")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """A canopy over rolling ground, some clearings, and a river winding through. Marks: 1 under the canopy."""
        ground = 0.04 * noise(rng, rows, columns, 1.2, step)
        canopy = smoothstep(0.66, 0.6, noise(rng, rows, columns, knobs["canopy_size"], step))  # clearings: noise high
        river = meander(rng, rows, columns, knobs["river_spacing"], 0.3, step)
        half_width = knobs["river_width"] / 2
        canopy *= smoothstep(half_width * 1.4, half_width * 2.2, river)  # open banks
        heights = ground + 0.045 * canopy
        heights = np.where(river < half_width, -0.005 - 0.03 * (1 - river / half_width), heights)
        return Shape(heights, canopy)
