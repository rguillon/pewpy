import math

import pytest

from pewpy.game.enemies.motions.forward import Forward
from tests.game.enemies.motions.moving import enemy, move


@pytest.mark.parametrize(("heading", "vx", "vy"), [(0.0, 0.5, 0.0), (math.pi / 2, 0.0, 0.5), (-math.pi / 2, 0.0, -0.5)])
def test_flying_the_way_it_is_heading(heading: float, vx: float, vy: float) -> None:
    flier = enemy(heading=heading)
    move(flier, Forward(speed=0.5))
    assert (flier.vx, flier.vy) == (pytest.approx(vx, abs=1e-12), pytest.approx(vy, abs=1e-12))
    assert flier.heading == heading
