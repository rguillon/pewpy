"""Rolling ground: wide low swells, for farmland."""

from pewpy.scenery.landscapes import Generator, Landscape, noise
from pewpy.scenery.params import Knobs
from pewpy.scenery.relief import Shape


class Rolling(Landscape):
    knobs = ("height", "swell_size", "detail_size")

    def shape(self, rng: Generator, rows: int, columns: int, max_height: float, step: float, knobs: Knobs) -> Shape:
        """Gently rolling ground for farmland: wide low swells, `height` high (`max_height` is for what stands on it,
        not used).
        """
        swells = noise(rng, rows, columns, knobs["swell_size"], step)
        detail = noise(rng, rows, columns, knobs["detail_size"], step)
        return Shape(knobs["height"] * (0.7 * swells + 0.3 * detail))
