"""Asteroids tumbling slowly, at one depth."""

import random

from pewpy.scenery.background.drift import Drifter, DriftLayer
from pewpy.scenery.ground.terrain import Area
from pewpy.scenery.params import RockLayer

ROCK_SHAPES = 6  # different asteroid models, see pewpy.graphics.models.background.rock


def rock_layer(rng: random.Random, layer: RockLayer, area: Area, spin_limit: float) -> DriftLayer:
    """`spin_limit`: the asteroids turn up to that fast, around each axis (degrees per second)."""

    def spin() -> float:
        return rng.uniform(-spin_limit, spin_limit)

    rocks = [
        Drifter(
            rng.uniform(area.left, area.right),
            rng.uniform(area.bottom, area.top),
            rng.uniform(*layer.size),
            layer.speed * rng.uniform(0.85, 1.15),
            shape=rng.randrange(ROCK_SHAPES),
            spin=(spin(), spin(), spin()),
            angle=(rng.uniform(0, 360), rng.uniform(0, 360), 0.0),
        )
        for _ in range(layer.count)
    ]
    return DriftLayer("rock", layer.depth, area, rocks, rng)
