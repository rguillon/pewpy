"""The Phantom, the player's light ship (nose up: y = 0 is the nose)."""

from pewpewdev.tools.models.parts import KEEP, engine, lights, ramp
from pewpewdev.tools.models.registry import SCALE
from pewpewdev.tools.models.sculpt import Model


def phantom() -> tuple[Model, list[dict] | None]:
    """Fast: a needle fuselage, a long canopy, a wide thin delta wing, one engine."""
    m = Model(15, 15, SCALE)
    m.materials["paint"] = (0.21, 0.56, 0.7)
    m.loft(
        (0, 14.5), lambda t: (ramp(t, 0.25, 1.6, 0.4), ramp(t, 0.25, 1.8, 0.4), ramp(t, -0.25, -1.0, 0.4), 0.8), "hull"
    )
    m.loft((3.0, 8.0), lambda t: (0.9 * (1 - abs(2 * t - 1) ** 4), 2.5 - abs(2 * t - 1) ** 2, 1.0, 0.5), "glass")
    m.paint(lambda x, y, z: abs(x - 7.5) < 0.5 and 4 <= y < 5 and z > 2.0, "glint")
    m.loft((8, 13), lambda _t: (0.5, 2.0, 1.0, 0.0), "hull_light")
    # The delta: thin, swept, lighter leading edge, paint panels near the tips.
    m.plate([(6.0, 6.0), (6.0, 13.0), (0.0, 13.0), (0.0, 11.5)], (0, 0), "hull")
    m.plate([(6.0, 6.0), (6.0, 7.0), (0.0, 12.5), (0.0, 11.5)], (0, 0), "hull_light")
    m.plate([(4.0, 9.5), (4.0, 12.0), (2.0, 12.0), (2.0, 11.0)], (0.5, 0.5), "paint")
    lights(m, 0.25, (12.0, 12.5), 0.5)
    # Small canted fins at the tail.
    m.fin(5.75, [(10.5, 0.5), (13.5, 0.5), (13.5, 2.5), (12.0, 2.5)], "hull", thickness=0.5)
    # The engine.
    m.nacelle(7.5, (12.5, 15), -0.25, 1.1, "frame")
    m.nacelle(7.5, (14.5, 15), -0.25, 0.7, "vent")
    m.finish(seams=(10,), keep=KEEP)
    return m, [engine(7, 14, 3.0, 11, "bottom", -0.25)]
