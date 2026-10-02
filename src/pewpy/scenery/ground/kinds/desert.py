"""The desert: dune ridges, rock mesas, oasis pools ringed with grass, and palms around them."""

import math
import random

import numpy as np

from pewpy.scenery.ground.landscapes import Flora, Generator, Landscape, inside, noise, scatter
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import Knobs


class Desert(Landscape):
    knobs = ("dune_spacing", "mesa_size", "pool_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Long dune ridges, flat-topped rock mesas, a few oasis pools ringed with grass (and palms, see `Palms`).
        Marks: 0 sand, 0.5 the grass around the pools, 1 rock.
        """
        crests = max(1, round(rows * step / knobs["dune_spacing"]))  # dune ridges per loop: whole, so they loop too
        y = np.arange(rows)[:, None] / rows
        x = np.arange(columns)[None, :] * step
        phase = 2 * math.pi * crests * y + 1.4 * x + 4 * noise(rng, rows, columns, 0.7, step)
        dune = (0.5 + 0.5 * np.sin(phase + 0.6 * np.sin(phase))) ** 2  # a gentle windward side, a steep slip face
        heights = 0.012 + dune * 0.3 * max_height
        mesas = noise(rng, rows, columns, knobs["mesa_size"], step)
        rock = smoothstep(0.74, 0.77, mesas)  # edges a few grid points wide: no jagged cliffs
        heights = np.maximum(heights, 0.6 * max_height * rock)  # a ledge around each mesa...
        heights = np.maximum(heights, max_height * smoothstep(0.79, 0.83, mesas))  # ...and its flat top
        pools = noise(rng, rows, columns, knobs["pool_size"], step)
        grass = (pools >= 0.14) & (pools < 0.19) & (rock < 0.5)  # a ring around the pool
        heights = np.where(grass, np.minimum(heights, 0.008), heights)
        heights = np.where((pools < 0.14) & (rock < 0.5), (pools - 0.14) * 0.6, heights)
        marks = np.where(rock > 0.5, 1.0, np.where(grass, 0.5, 0.0))
        return Shape(heights, marks)


class Palms(Flora):
    knobs = ("chance", "size", "height")

    def props(self, rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
        """Palms on the grass around the desert's oases (on a share `chance` of its points)."""
        marks = shape.marks if shape.marks is not None else np.zeros_like(shape.heights)
        rows = shape.heights.shape[0]
        size = knobs["size"]
        return [
            Prop("palm", x, y, size, size, rng.uniform(*knobs["height"]), rng.randrange(1 << 30))
            for x, y in scatter(rng, np.abs(marks - 0.5) < 0.1, knobs["chance"], step_x, step_y)
            if inside(y, 0.02, rows, step_y)
        ]
