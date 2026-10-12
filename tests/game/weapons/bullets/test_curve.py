import math

import pytest

from pewpy.game.weapons.bullets.curve import CURVE_TIME, CurveBullet


def test_a_curving_shot_bends_counterclockwise_then_flies_straight() -> None:
    shot = CurveBullet(vx=0.0, vy=-0.5, turn_rate=90.0, bend_time=1.0)
    shot.move(0.5)
    assert math.degrees(math.atan2(shot.vy, shot.vx)) == pytest.approx(-90 + 45)
    shot.move(1.0)  # bends only its last half second
    assert math.degrees(math.atan2(shot.vy, shot.vx)) == pytest.approx(0.0, abs=1e-9)
    shot.move(1.0)
    assert (shot.vx, shot.vy) == (pytest.approx(0.5), pytest.approx(0.0, abs=1e-9))


def test_shots_bend_for_a_while_unless_told() -> None:
    assert CurveBullet().bend_time == CURVE_TIME
