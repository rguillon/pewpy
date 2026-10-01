"""Level ground: nearly flat, for the city and the refinery."""

from pewpy.scenery.landscapes import Generator, Landscape, noise
from pewpy.scenery.params import Knobs
from pewpy.scenery.relief import Shape


class LevelGround(Landscape):
    knobs = ("height", "size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Nearly flat ground for the city and the refinery, just not perfectly even (`height`)."""
        return Shape(knobs["height"] * noise(rng, rows, columns, knobs["size"], step))
