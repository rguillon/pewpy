import math

import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets.missile import Missile


def test_a_homing_missile_turns_towards_the_nearest_target_at_its_turn_rate() -> None:
    missile = Missile(x=0.0, y=0.0, vy=0.5, homing=True, turn_rate=1.0)
    near, far = Entity(x=0.3, y=0.0), Entity(x=-1.0, y=0.0)
    missile.steer(0.1, [far, near])
    assert math.atan2(missile.vy, missile.vx) == pytest.approx(math.pi / 2 - 0.1)
    assert math.hypot(missile.vx, missile.vy) == pytest.approx(0.5)


def test_a_missile_flies_straight_without_homing_or_targets() -> None:
    plain = Missile(vy=0.5, turn_rate=1.0)
    plain.steer(0.1, [Entity(x=1.0)])
    lost = Missile(vy=0.5, homing=True, turn_rate=1.0)
    lost.steer(0.1, [])
    assert (plain.vx, plain.vy) == (lost.vx, lost.vy) == (0.0, 0.5)


def test_a_missile_is_drawn_as_one() -> None:
    assert Missile.drawing == "missile"
