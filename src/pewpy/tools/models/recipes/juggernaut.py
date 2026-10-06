"""The Juggernaut, the player's heavy ship (nose up: y = 0 is the nose)."""

from pewpy.tools.models.parts import KEEP, engine, lights, ramp
from pewpy.tools.models.registry import SCALE
from pewpy.tools.models.sculpt import Model


def juggernaut() -> tuple[Model, list[dict] | None]:
    """Heavy armor: a broad armored hull with a raised ridge, two big side pods, three engines."""
    m = Model(21, 21, SCALE)
    m.materials["paint"] = (0.212, 0.468, 0.85)
    # Main hull: a blunt prow, then broad and flat.
    m.loft((0, 19.5), lambda t: (ramp(t, 1.5, 4.5, 0.3), ramp(t, 1.0, 2.5, 0.25), -2.0, 1.5), "hull")
    # The armored ridge down the middle, the cockpit set into it.
    m.loft((1, 17), lambda t: (ramp(t, 0.6, 1.2, 0.2), ramp(t, 2.0, 4.0, 0.25), 1.0, 0.5), "hull_light")
    m.loft((4, 8), lambda _t: (1.3, 3.6, 2.0, 0.6), "glass")
    m.paint(lambda x, y, z: abs(x - 10.5) < 0.5 and 5 <= y < 6 and z > 3, "glint")
    # Side pods: heavy armored blocks, ribbed, paint on their tops.
    m.loft((5, 19.5), lambda _t: (1.8, 1.8, -1.8, 0.8), "hull", center=4.0)
    for row in range(7, 19, 2):
        m.loft((row, row + 0.5), lambda _t: (1.95, 1.95, -1.95, 0.8), "frame", center=4.0)
    m.paint(lambda x, y, z: abs(x - 4.0) < 0.6 and 6 <= y < 17 and z > 1.4, "paint")
    # Stub wings with guns, lights at the tips.
    m.plate([(2.2, 10.0), (2.2, 16.0), (0.0, 15.0), (0.0, 11.0)], (0, 0), "hull")
    m.fill(lambda x, y, z: x < 1.0 and 8.0 <= y < 12 and 0 <= z < 0.5, (0, 1, 8, 12, -1, 1), "metal")
    lights(m, 0.25, (11.0, 11.5), 0.5)
    # Engines: three nozzles at the back.
    for x in (4.5, 10.5):
        m.nacelle(x, (19.5, 21), -0.25, 1.3, "frame")
        m.nacelle(x, (20.5, 21), -0.25, 0.9, "vent")
    m.finish(seams=(9, 13, 16), keep=KEEP)
    return m, [
        engine(10, 20, 3.2, 10, "bottom", -0.25),
        engine(4, 20, 3.2, 9, "bottom", -0.25),
        engine(16, 20, 3.2, 9, "bottom", -0.25),
    ]
