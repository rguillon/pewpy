"""Islands in a sea, shelving into shallows around them."""

import numpy as np

from pewpy.scenery.landscapes import Generator, Landscape, level_for_share, noise
from pewpy.scenery.params import Knobs
from pewpy.scenery.relief import Shape


class Islands(Landscape):
    knobs = ("land_share", "size", "detail_size", "fine_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Islands in a sea (`land_share` of it), shelving into shallows around them."""
        value = 0.65 * noise(rng, rows, columns, knobs["size"], step)
        value += 0.25 * noise(rng, rows, columns, knobs["detail_size"], step)
        value += 0.1 * noise(rng, rows, columns, knobs["fine_size"], step)
        sea = level_for_share(value, knobs["land_share"])
        peak = float(np.max(value))
        land = np.clip((value - sea) / max(peak - sea, 1e-9), 0.0, 1.0) ** 0.8 * max_height
        return Shape(np.where(value > sea, land, (value - sea) * 0.7))
