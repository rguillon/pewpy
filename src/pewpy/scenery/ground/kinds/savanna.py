"""A savanna: golden grassland gently rolling, dry sandy riverbeds winding through it, rock outcrops, trees."""

import random

import numpy as np

from pewpy.scenery.ground.landscapes import Flora, Generator, Landscape, inside, meander, noise, scatter
from pewpy.scenery.ground.relief import Shape, smoothstep
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import Knobs

RIVERBED = 0.07  # world units: a dry riverbed's half width


class Savanna(Landscape):
    """Grassland with dry riverbeds and rock outcrops."""

    knobs = ("size", "bend_spacing", "outcrop_share")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Shape gently rolling grassland, a dry riverbed winding down it, and rock outcrops.

        Swells `size` across, a bend of the riverbed every `bend_spacing`, outcrops on `outcrop_share` of it.
        Marks: 0 grass, 0.5 the riverbed's sand, 1 rock.
        """
        heights = 0.006 + 0.15 * max_height * noise(rng, rows, columns, knobs["size"], step)
        bed = smoothstep(RIVERBED, RIVERBED * 0.6, meander(rng, rows, columns, knobs["bend_spacing"], 0.3, step))
        heights = heights * (1 - 0.7 * bed)
        rocks = noise(rng, rows, columns, 0.1, step)  # small: kopjes, piles of boulders
        level = float(np.percentile(rocks, 100 * (1 - knobs["outcrop_share"])))
        outcrop = smoothstep(level, level + 0.06, rocks) * (1 - bed)
        heights = heights + 0.5 * max_height * outcrop
        marks = np.where(outcrop > 0.3, 1.0, np.where(bed > 0.5, 0.5, 0.0))
        return Shape(heights, marks)


class Acacias(Flora):
    """Trees standing alone on the savanna's grass, more of them along its riverbed."""

    knobs = ("chance", "size", "height")

    def props(self, rng: random.Random, shape: Shape, step_x: float, step_y: float, knobs: Knobs) -> list[Prop]:
        """Trees on the grass (on a share `chance` of its points), three times as many near the riverbed."""
        marks = shape.marks if shape.marks is not None else np.zeros_like(shape.heights)
        rows = shape.heights.shape[0]
        size = knobs["size"]
        grass = marks < 0.25
        near_bed = grass & (np.roll(marks, 3, axis=1) == 0.5) | grass & (np.roll(marks, -3, axis=1) == 0.5)
        places = scatter(rng, grass & ~near_bed, knobs["chance"], step_x, step_y)
        places += scatter(rng, near_bed, min(1.0, 3 * knobs["chance"]), step_x, step_y)
        return [
            Prop("tree", x, y, size, size, rng.uniform(*knobs["height"]), rng.randrange(1 << 30))
            for x, y in places
            if inside(y, 0.02, rows, step_y)
        ]
