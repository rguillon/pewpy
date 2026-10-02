import random

import numpy as np

from pewpy.scenery.ground import landscapes


def seeded(seed: int) -> random.Random:
    return random.Random(seed)


def test_scattering_is_random_but_reproducible() -> None:
    where = np.ones((10, 10), dtype=bool)
    first = landscapes.scatter(seeded(1), where, 0.5, 0.02, 0.02)
    assert first == landscapes.scatter(seeded(1), where, 0.5, 0.02, 0.02)
    assert 20 < len(first) < 80
