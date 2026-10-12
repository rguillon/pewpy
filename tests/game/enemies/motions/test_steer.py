import math

import pytest

from pewpy.game.enemies.motions.steer import Steer
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity
from tests.game.enemies.motions.moving import DT, SCROLL, TARGET, enemy, move


def test_steering_towards_the_player_or_down() -> None:
    missile = enemy(y=0.5, heading=math.pi / 2)  # launched upwards
    move(missile, Steer(rate=math.radians(100), speed=0.45), 3.0, Entity(x=0.3, y=-0.75))
    assert missile.vy < 0
    assert math.hypot(missile.vx, missile.vy) == pytest.approx(0.45)
    swarmer = enemy(x=0.0, heading=0.0)
    move(swarmer, Steer(goal="down", rate=0.9, widen=True, inside=True, speed=0.6), 5.0)
    assert swarmer.heading == pytest.approx(-math.pi / 2)


def test_a_steering_enemy_can_wait_to_be_inside_the_screen() -> None:
    outside = enemy(x=-HALF_WIDTH - 0.2, heading=0.0)
    Steer(goal="down", rate=1.0, inside=True, speed=0.6).apply(outside, DT, TARGET, SCROLL)
    assert outside.heading == 0.0
    assert outside.vx == pytest.approx(0.6)
