"""A dusty planet: low eroded hills pocked with craters."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, normalized, wrapped_distance
from pewpy.scenery.ground.relief import Shape, eroded_noise
from pewpy.scenery.params import Knobs


class Hills(Landscape):
    knobs = ("size", "crater_spacing", "crater_radius")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """A dusty planet: low eroded hills pocked with craters (one per `crater_spacing` of the loop). Marks: the
        craters' rims and the dust thrown out.
        """
        value = normalized(eroded_noise(rng, rows, columns, knobs["size"] / step, octaves=6))
        rims = np.zeros_like(value)
        for _ in range(max(1, round(rows * step / knobs["crater_spacing"]))):
            radius = rng.uniform(*knobs["crater_radius"])
            distance = wrapped_distance(
                rows, columns, step, rng.uniform(0, columns * step), rng.uniform(0, rows * step)
            )
            d = distance / radius
            value -= 0.55 * np.clip(1 - d * d, 0.0, 1.0)  # the bowl
            rim = np.exp(-(((d - 1.05) / 0.18) ** 2))
            value += 0.22 * rim
            rims = np.maximum(rims, rim + 0.4 * np.exp(-d) * (d > 1))
        return Shape(max_height * np.clip(value, 0.0, 1.0), np.clip(rims, 0.0, 1.0))
