import pytest

from pewpy.game.enemies.motions.accelerate import Accelerate
from tests.game.enemies.motions.moving import enemy, move


def test_speeding_up_to_a_top_speed() -> None:
    rocket = enemy(vy=-0.25)
    move(rocket, Accelerate(rate=1.0, top=1.1), 0.1)
    assert -1.1 < rocket.vy < -0.25
    move(rocket, Accelerate(rate=1.0, top=1.1), 2.0)
    assert rocket.vy == pytest.approx(-1.1)


def test_standing_still_it_has_no_way_to_speed_up() -> None:
    still = enemy()
    move(still, Accelerate(rate=1.0, top=1.1), 0.5)
    assert (still.vx, still.vy) == (0.0, 0.0)
