"""Level ground: nearly flat, for the city and the refinery."""

from pewpy.scenery.ground.landscapes import Generator, Landscape, noise
from pewpy.scenery.ground.relief import Shape
from pewpy.scenery.params import Knobs


class LevelGround(Landscape):
    knobs = ("height", "size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Nearly flat ground for the city and the refinery, just not perfectly even (`height`)."""
        return Shape(knobs["height"] * noise(rng, rows, columns, knobs["size"], step))
