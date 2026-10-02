"""The Drone (enemies fly down: y = 0 is the tail, their nose at the bottom)."""

from pewpewdev.tools.models.parts import KEEP, engine, lights
from pewpewdev.tools.models.registry import SCALE
from pewpewdev.tools.models.sculpt import Model


def drone() -> tuple[Model, list[dict] | None]:
    """Build a small attack drone: an armored octagonal body, a red sensor eye, four weapon pods, one engine."""
    m = Model(15, 15, SCALE)
    m.materials["paint"] = (0.8, 0.16, 0.12)
    m.materials["eye"] = (1.0, 0.2, 0.1)
    octagon = [(4.5, 1.0), (10.5, 1.0), (14.0, 4.5), (14.0, 10.5), (10.5, 14.0), (4.5, 14.0), (1.0, 10.5), (1.0, 4.5)]
    m.plate(octagon, (-1, 0), "hull", mirror=False)
    # The raised core, chamfered, with the eye at its front.
    m.loft((3.5, 12.5), lambda _t: (3.0, 2.0, 0.5, 1.2), "hull_light")
    m.loft((5.5, 10.5), lambda _t: (1.6, 2.6, 1.0, 0.8), "hull")
    m.fill(lambda x, y, z: abs(x - 7.5) < 1.2 and 10.0 <= y < 11.5 and 1.0 <= z < 2.5, (6, 9, 10, 12, 0, 3), "eye")
    # A red band around the core.
    m.paint(lambda x, y, z: z > 0.6 and (4.0 <= y < 4.6 or 11.4 <= y < 12.0) and abs(x - 7.5) < 3, "paint")
    # Weapon pods on the sides, their muzzles forward.
    for x in (1.8,):
        m.nacelle(x, (4.5, 11.5), -0.5, 1.2, "frame")
        m.nacelle(x, (11.5, 13.5), -0.5, 0.5, "metal")
    m.paint(lambda x, y, z: x < 3.0 and 6 <= y < 9 and z > 0.4, "paint")
    lights(m, 1.0, (7.0, 8.0), 0.5)
    # The engine at the back.
    m.nacelle(7.5, (0, 3.5), 0.0, 1.3, "frame")
    m.nacelle(7.5, (0, 0.5), 0.0, 0.9, "vent")
    m.finish(seams=(7.5,), keep=KEEP | {"eye"})
    return m, [engine(7, 0, 3.2, 6, "top")]
