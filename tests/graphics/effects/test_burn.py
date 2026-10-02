import random

import pytest

from pewpy.graphics.effects.burn import BURN_SPARKS, Burn


def test_laser_burn_makes_sparks_at_a_steady_rate() -> None:
    rng = random.Random(4)
    count = sum(len(Burn(0.0, 0.5, 1 / 60).particles(rng)) for _ in range(600))
    assert count == pytest.approx(BURN_SPARKS * 10, rel=0.15)
