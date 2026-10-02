"""A distant planet, on the left or the right, turning slowly."""

import random

from pewpy.scenery.background.drift import Drifter, DriftLayer
from pewpy.scenery.ground.terrain import Area
from pewpy.scenery.params import DistantPlanet


def planet_layer(rng: random.Random, planet: DistantPlanet, area: Area) -> DriftLayer:
    """Make the distant planet's layer: one big planet on the left or the right."""
    side = rng.choice((0.25, 0.75))  # left or right
    size = rng.uniform(*planet.size)
    drifter = Drifter(area.left + area.width * side, area.top - area.height * 0.25, size, planet.speed)
    drifter.spin = (planet.spin, 0.0, 0.0)
    return DriftLayer("planet", planet.depth, area, [drifter], rng)
