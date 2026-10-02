"""Pack ice: floes split by leads of open water, and a few icebergs."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, level_for_share, noise
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.params import Knobs


class PackIce(Landscape):
    knobs = ("open_water", "berg_share", "floe_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Floes of sea ice split by dark leads of open water, and a few icebergs. Marks: 1 on the icebergs."""
        value = 0.7 * noise(rng, rows, columns, knobs["floe_size"], step) + 0.3 * noise(rng, rows, columns, 0.2, step)
        sea = level_for_share(value, knobs["open_water"])
        leads = 1 - np.abs(2 * noise(rng, rows, columns, 0.35, step) - 1)  # a network of cracks where this is high
        floe = smoothstep(sea, sea + 0.04, value) * smoothstep(0.96, 0.9, leads)
        heights = np.where(floe > 0.2, 0.014 * floe - 0.002, -0.004 - np.maximum(sea - value, 0.0) * 0.5)
        berg_level = level_for_share(value, knobs["berg_share"])
        peak = float(np.max(value))
        berg = np.clip((value - berg_level) / max(peak - berg_level, 1e-9), 0.0, 1.0)
        heights = np.where(berg > 0, 0.03 + np.sqrt(berg) * 0.8 * max_height, heights)
        return Shape(heights, (berg > 0).astype(np.float64))
