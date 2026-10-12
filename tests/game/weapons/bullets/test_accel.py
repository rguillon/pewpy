import math

import pytest

from pewpy.game.weapons.bullets.accel import AccelBullet


def test_an_accel_shot_speeds_up_its_way_to_its_top_speed() -> None:
    shot = AccelBullet(vx=0.3, vy=-0.4, rate=1.0, top_speed=1.0)
    shot.move(0.1)
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.6)
    assert shot.vx / shot.vy == pytest.approx(-0.75)  # still the same way
    shot.move(1.0)
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(1.0)


def test_a_still_shot_stays_still() -> None:
    shot = AccelBullet(rate=1.0)
    shot.move(0.5)
    assert (shot.vx, shot.vy, shot.x, shot.y) == (0.0, 0.0, 0.0, 0.0)
