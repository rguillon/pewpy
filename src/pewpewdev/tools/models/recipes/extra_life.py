"""The extra life pickup."""

from pewpewdev.tools.models.parts import ramp
from pewpewdev.tools.models.registry import SCALE
from pewpewdev.tools.models.sculpt import Model


def extra_life() -> tuple[Model, list[dict] | None]:
    """Build the extra life: a green gem with a little white ship standing on it."""
    m = Model(12, 12, SCALE)
    m.materials["paint"] = (0.2, 0.8, 0.35)
    m.materials["paint_light"] = (0.45, 0.95, 0.55)
    m.materials["white"] = (0.95, 0.96, 0.97)
    octagon = [(3.5, 0.5), (8.5, 0.5), (11.5, 3.5), (11.5, 8.5), (8.5, 11.5), (3.5, 11.5), (0.5, 8.5), (0.5, 3.5)]
    inner = [(4.0, 2.0), (8.0, 2.0), (10.0, 4.0), (10.0, 8.0), (8.0, 10.0), (4.0, 10.0), (2.0, 8.0), (2.0, 4.0)]
    m.plate(octagon, (-1, 1), "paint", mirror=False)
    m.plate(inner, (2, 2), "paint_light", mirror=False)  # a raised facet
    # The ship: a fuselage, swept wings, on the facet.
    m.loft((2.5, 9.5), lambda t: (ramp(t, 0.3, 1.0, 0.4), 3.6, 2.5, 0.3), "white")
    m.plate([(5.5, 5.5), (5.5, 9.0), (2.5, 9.5), (2.5, 8.0)], (3, 3), "white")
    m.paint(lambda x, y, z: abs(x - 6.0) < 0.6 and 4 <= y < 5 and z > 3.2, "glint")
    return m, None
