"""A canyon: a plateau cut by a winding gorge with stepped cliffs, sandbanks and a river."""

import numpy as np

from pewpy.scenery.ground.landscapes import Generator, Landscape, meander, noise
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.params import Knobs


class Canyon(Landscape):
    knobs = ("bend_spacing", "river", "floor", "wall", "steps")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """A plateau cut by a winding canyon: stepped cliffs, sandbanks, a river at the bottom. Marks: 0.5 sand. The
        river, the canyon's floor and its walls reach `river`, `floor` and `floor + wall` from its middle.
        """
        plateau = max_height * (0.85 + 0.15 * noise(rng, rows, columns, 0.7, step))
        distance = meander(rng, rows, columns, knobs["bend_spacing"], 0.22, step)
        distance = distance + 0.05 * (noise(rng, rows, columns, 0.3, step) - 0.5)  # ragged walls
        water, floor, wall, steps = knobs["river"], knobs["floor"], knobs["wall"], knobs["steps"]
        t = np.clip((distance - floor) / wall, 0.0, 1.0) * steps
        stairs = (np.floor(t) + smoothstep(0.7, 1.0, t - np.floor(t))) / steps  # flat ledges, steep risers
        heights = np.where(distance < floor, 0.01, plateau * np.minimum(stairs, 1.0))
        heights = np.where(distance < water, -0.004 - 0.025 * (1 - distance / water), heights)
        marks = np.where((distance >= water) & (distance < floor), 0.5, 0.0)
        return Shape(heights, marks)
