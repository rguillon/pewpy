"""Nebulas: a few dim clouds far away in space."""

import random

from pewpy.scenery.background.drift import Drifter, DriftLayer
from pewpy.scenery.ground.terrain import Area
from pewpy.scenery.params import Nebulas


def nebula_layer(rng: random.Random, nebulas: Nebulas, area: Area) -> DriftLayer:
    count = nebulas.count
    clouds = [
        Drifter(
            rng.uniform(area.left, area.right),
            area.bottom + area.height * (i + rng.random()) / count,
            rng.uniform(*nebulas.size),
            nebulas.speed,
            shape=i % 3,  # its color, see view.py
        )
        for i in range(count)
    ]
    return DriftLayer("cloud", nebulas.depth, area, clouds, rng)
