"""Mountains: eroded ranges with sharp crests and flat valley floors."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, normalized
from pewpy.scenery.ground.relief import Shape, eroded_noise, ridged_mountains, smoothstep
from pewpy.scenery.params import Knobs


class Mountains(Landscape):
    """Mountains: eroded ranges with sharp crests."""

    knobs = ("range_size", "crest_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape eroded ranges (about `range_size` apart), sharp crests (`crest_size`) and flat valleys between them."""
        ranges = eroded_noise(rng, rows, columns, knobs["range_size"] / step)
        crests = ridged_mountains(rng, rows, columns, knobs["crest_size"] / step, octaves=5)
        middle, top = np.percentile(ranges, 40), np.percentile(ranges, 90)
        value = ranges + 0.6 * crests * smoothstep(middle, top, ranges)  # sharp crests on the high ground only
        value = normalized(value, 3, 99.7)  # the lowest 3 % flat: valley floors
        return Shape(max_height * value**1.4)
