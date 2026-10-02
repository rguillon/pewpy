"""See-through clouds drifting between the ground and the ships, blown sideways."""

import random

from pewpy.scenery.background.drift import Drifter, DriftLayer
from pewpy.scenery.ground.terrain import Area
from pewpy.scenery.params import Mist


def mist_layer(
    rng: random.Random, area: Area, speed_factor: float, mist: Mist, depth: float, amount: float, wind: float
) -> DriftLayer:
    """`amount`: from 0 (none) to 1 (`mist.count` clouds)."""
    count = round(amount * mist.count)
    drifters = [
        Drifter(
            rng.uniform(area.left, area.right),
            area.bottom + area.height * (i + rng.random()) / max(count, 1),  # spread out from the start
            rng.uniform(*mist.size),
            speed_factor * rng.uniform(0.9, 1.1),
            shape=rng.randrange(1000),  # its texture and how see-through it is, see view.py
            angle=(0.0, 0.0, rng.uniform(0, 360)),
            wind=wind * rng.uniform(0.8, 1.2),
        )
        for i in range(count)
    ]
    return DriftLayer("mist", depth, area, drifters, rng)
