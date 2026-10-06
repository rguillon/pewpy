"""The Gunship (enemies fly down: y = 0 is the tail, their nose at the bottom)."""

from pewpy.tools.models.parts import KEEP, engine, lights, ramp, ribbed
from pewpy.tools.models.registry import SCALE
from pewpy.tools.models.sculpt import Model


def gunship() -> tuple[Model, list[dict] | None]:
    """Build a heavy gunship: a broad armored hull, a bridge, engine pods on outriggers, a big cannon at the front."""
    m = Model(29, 21, SCALE)
    m.materials["paint"] = (0.62, 0.13, 0.1)
    # The hull: wide, its front corners cut.
    m.loft((2, 16), lambda t: (ramp(t, 9.5, 9.5), 2.0, -2.0, 1.5), "hull")
    m.plate([(5.0, 14.0), (14.5, 14.0), (14.5, 16.5), (8.0, 16.5)], (-1, 1), "hull")
    # A raised deck and the bridge.
    m.loft((3, 13), lambda _t: (5.5, 3.0, 1.0, 1.0), "hull_light")
    m.loft((6.5, 10.5), lambda _t: (2.4, 4.0, 2.0, 0.8), "hull")
    m.box((13, 15), (9.5, 9.5), (3.5, 3.5), "glass", mirror=False)
    m.paint(lambda x, y, z: abs(x - 14.5) < 0.5 and 9.5 <= y < 10.5 and z > 3.2, "glint")
    # Armor plates on the deck's sides, vents between them, red markings.
    for y0 in (3.5, 7.0, 10.5):
        m.box((5.5, 8.5), (y0, y0 + 2.5), (2.5, 3), "hull")
    m.box((6, 8), (6.25, 6.25), (2.5, 2.5), "vent")
    m.box((6, 8), (9.75, 9.75), (2.5, 2.5), "vent")
    m.paint(lambda x, y, z: 5.5 <= x < 8.5 and 13 <= y < 14 and z > 1.6, "paint")
    m.paint(lambda x, y, z: 9.0 <= x < 9.5 and 3 <= y < 13 and z > 2.2, "paint")
    m.paint(lambda x, y, z: x < 5.0 and 2 <= y < 3.5 and z > 0.5, "paint")
    # Outriggers to the engine pods.
    m.box((4, 5), (6, 10), (-0.5, 0), "frame")
    m.box((0, 4), (7, 9), (0, 0), "hull_dark")
    ribbed(m, 2.5, (0, 9), 0.0, 1.7)
    m.nacelle(2.5, (0, 0.5), 0.0, 1.2, "vent")
    lights(m, 0.25, (8.0, 8.5), 0.5)
    # The cannon: a thick barrel forward, a muzzle.
    m.nacelle(14.5, (15, 20), -0.5, 0.9, "frame", mirror=False)
    m.nacelle(14.5, (20, 21), -0.5, 0.5, "metal", mirror=False)
    # Side guns.
    m.nacelle(8.0, (16.5, 19), -0.5, 0.45, "metal")
    m.finish(seams=(6, 12), keep=KEEP)
    return m, [engine(2, 0, 3.6, 7, "top"), engine(26, 0, 3.6, 7, "top")]
