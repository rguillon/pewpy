"""The Vanguard, the player's balanced ship (nose up: y = 0 is the nose)."""

from pewpewdev.tools.models.parts import ramp
from pewpewdev.tools.models.registry import SCALE
from pewpewdev.tools.models.sculpt import Model


def vanguard() -> tuple[Model, list[dict] | None]:
    """Balanced: a pointed fuselage with a bubble canopy, swept wings, two ribbed engine nacelles."""
    m = Model(17, 18, SCALE)
    m.materials["paint"] = (0.25, 0.55, 1.0)
    # Fuselage: a pointed nose widening into the body; a raised back that slopes down to the tail.
    m.loft(
        (0, 16.5),
        lambda t: (
            ramp(t, 0.3, 2.3, 0.45),
            ramp(t, 0.5, 2.0, 0.35) - max(0.0, t - 0.8) * 2.5,
            ramp(t, -0.2, -1.5, 0.45),
            1.2,
        ),
        "hull",
    )
    # Canopy: a bubble of dark glass, its glint, a frame behind it.
    m.loft((4.0, 9.5), lambda t: (1.4 * (1 - abs(2 * t - 1) ** 4), 3.2 - abs(2 * t - 1) ** 2 * 1.2, 1.0, 0.7), "glass")
    m.paint(lambda x, y, z: abs(x - 8.5) < 0.5 and 5.0 <= y < 6.0 and z > 2.5, "glint")
    m.loft((9.5, 10.0), lambda t: (1.3, 2.7, 1.0, 0.5), "frame")
    # Spine along the back, a dorsal sensor behind it.
    m.loft((10, 15.5), lambda t: (0.5, 2.6 - t * 0.6, 1.5, 0.0), "hull_light")
    # Side intakes, dark, along the cockpit.
    m.box((6, 6), (8, 10), (0, 1), "vent")
    # Swept wings: thin, the tips rising a little, a lighter leading edge, a paint stripe, lights at the tips.
    wing = [(6.5, 7.0), (6.5, 15.0), (0.5, 14.0), (0.5, 11.5)]
    m.plate(wing, lambda x, y: (0, 0 if x > 3 else 0.5), "hull")
    m.plate([(6.5, 7.0), (6.5, 8.0), (0.5, 12.5), (0.5, 11.5)], lambda x, y: (0, 0 if x > 3 else 0.5), "hull_light")
    m.plate([(5.5, 11.0), (5.5, 12.0), (1.5, 13.0), (1.5, 12.0)], (0.5, 0.5), "paint")
    m.fill(lambda x, y, z: x < 0.5 and 12.0 <= y < 13.0 and 0 <= z < 1, (0, 1, 11, 14, 0, 1), "light")
    # Engine nacelles under the wing roots: ribbed, with dark nozzles.
    m.nacelle(5.5, (9, 17.5), -0.75, 1.6, "hull")
    for row in (11, 12.5, 14, 15.5):
        m.nacelle(5.5, (row, row + 0.5), -0.75, 1.75, "frame")
    m.nacelle(5.5, (17.5, 18), -0.75, 1.2, "vent")
    m.nacelle(5.5, (8.5, 9.5), -0.75, 1.1, "vent")  # intake at the front
    # Guns: short barrels at the wing roots.
    m.fill(lambda x, y, z: 6.0 <= x < 6.5 and 5.0 <= y < 8.0 and -0.5 <= z < 0, (6, 7, 5, 8, -1, 0), "metal")
    m.finish(seams=(10, 13), keep=frozenset({"glass", "glint", "paint", "light", "vent", "metal"}))
    return m, [
        {"x": 5, "y": 17, "width": 3.2, "length": 9, "towards": "bottom", "z": -0.75},
        {"x": 11, "y": 17, "width": 3.2, "length": 9, "towards": "bottom", "z": -0.75},
    ]
