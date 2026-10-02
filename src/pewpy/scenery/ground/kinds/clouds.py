"""A cloud deck, with the dark ground far below through its gaps."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, level_for_share, noise
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.params import Knobs


class Clouds(Landscape):
    """A deck of low clouds over the dark ground far below."""

    knobs = ("cover", "size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape a deck of low clouds (`cover`: the share it covers); gaps (below 0) show the ground far below."""
        value = 0.7 * noise(rng, rows, columns, knobs["size"], step) + 0.3 * noise(rng, rows, columns, 0.28, step)
        cover = level_for_share(value, knobs["cover"])
        peak = float(np.max(value))
        rise = np.clip((value - cover) / max(peak - cover, 1e-9), 0.0, 1.0)
        puffs = rise**0.4 * smoothstep(0.0, 0.12, rise) * max_height  # round puffs, their edges rounded off too
        return Shape(np.where(value > cover, puffs, -0.002 - (cover - value) * 0.3))
