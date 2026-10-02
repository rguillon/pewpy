"""The Bomber (enemies fly down: y = 0 is the tail, their nose at the bottom)."""

from pewpewdev.tools.models.parts import KEEP, engine, lights, ramp, ribbed
from pewpewdev.tools.models.registry import SCALE
from pewpewdev.tools.models.sculpt import Model


def bomber() -> tuple[Model, list[dict] | None]:
    """A bomber: a broad flying wing, four engine pods at the back, a bomb bay under a raised hull."""
    m = Model(33, 18, SCALE)
    m.materials["paint"] = (0.34, 0.51, 0.255)
    # The wing: swept back from the nose (enemies fly down: the nose is at the bottom).
    m.plate(
        [(16.5, 17.0), (16.5, 3.0), (0.0, 3.0), (0.0, 4.5), (9.0, 16.5)], lambda x, y: (0, 0 if x < 10 else 0.5), "hull"
    )
    m.plate([(16.5, 17.0), (9.0, 16.5), (0.0, 4.5), (0.0, 4.0), (9.0, 15.8), (16.5, 16.4)], (0, 0.5), "hull_light")
    # The central hull, raised, with the bay.
    m.loft((2.5, 17.0), lambda t: (ramp(t, 6.0, 1.5, 1.0), ramp(t, 2.5, 1.5, 1.0), -1.5, 1.2), "hull")
    m.loft((7, 12), lambda t: (2.0, 2.8, 2.0, 0.6), "vent")
    m.paint(lambda x, y, z: 11.0 <= x < 12.0 and 4 <= y < 15 and z > 1.5, "paint")
    # Chevrons on the wings, the color of the old bomber.
    m.paint(
        lambda x, y, z: 3.0 <= x < 10.0 and 5.0 + (10.0 - x) * 0.55 <= y < 6.0 + (10.0 - x) * 0.55 and z > -0.1, "paint"
    )
    m.paint(
        lambda x, y, z: 3.0 <= x < 10.0 and 7.0 + (10.0 - x) * 0.55 <= y < 7.5 + (10.0 - x) * 0.55 and z > -0.1, "paint"
    )
    lights(m, 0.25, (3.5, 4.5), 0.5)
    # Four engine pods at the back.
    for x in (6.5, 13.5):
        ribbed(m, x, (0, 5), 0.0, 1.5)
        m.nacelle(x, (0, 0.5), 0.0, 1.0, "vent")
    m.finish(seams=(9, 13), keep=KEEP)
    return m, [
        engine(6, 0, 3, 7, "top"),
        engine(13, 0, 3, 7, "top"),
        engine(19, 0, 3, 7, "top"),
        engine(26, 0, 3, 7, "top"),
    ]
