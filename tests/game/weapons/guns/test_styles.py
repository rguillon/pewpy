import math
from typing import Any

import pytest

from pewpy import config
from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import AccelBullet, Bullet, CurveBullet, Missile, WaveBullet
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.styles import ACCEL_START, ACCEL_TOP, BULLET_SIZES, HEAVY_BULLET_SIZE, styled_bullet

DT = 1 / 60


def styled(**gun: Any) -> Bullet:  # noqa: ANN401
    return styled_bullet(Gun("fan", interval=1.0, speed=0.5, **gun), Entity(x=0.1, y=0.2), 0.0, -0.5)


def test_a_plain_shot_flies_from_its_source_hostile_and_normal_sized() -> None:
    shot = styled()
    assert type(shot) is Bullet
    assert (shot.x, shot.y, shot.vx, shot.vy) == (0.1, 0.2, 0.0, -0.5)
    assert (shot.width, shot.damage, shot.hostile, shot.style) == (
        config.ENEMY_BULLET_SIZE,
        config.ENEMY_BULLET_DAMAGE,
        True,
        "normal",
    )


def test_heavy_shots_are_bigger_and_pellets_smaller() -> None:
    assert styled(style="heavy").width == HEAVY_BULLET_SIZE == BULLET_SIZES["heavy"]
    assert styled(style="pellet").width < config.ENEMY_BULLET_SIZE


def test_a_gun_can_give_its_shots_size_and_damage() -> None:
    shot = styled(size=(0.02, 0.06), damage=3.0)
    assert (shot.width, shot.height, shot.damage) == (0.02, 0.06, 3.0)


def test_accelerating_shots_start_slow_and_speed_up() -> None:
    shot = styled(style="accel")
    assert isinstance(shot, AccelBullet)
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5 * ACCEL_START)
    for _ in range(300):
        shot.move(DT)
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5 * ACCEL_TOP)


def test_curving_shots_bend() -> None:
    shot = styled(style="curve", curve=90)
    assert isinstance(shot, CurveBullet)
    for _ in range(60):
        shot.move(DT)
    assert shot.vx == pytest.approx(0.5, abs=0.01)  # a quarter turn in a second, counterclockwise
    assert math.hypot(shot.vx, shot.vy) == pytest.approx(0.5)


def test_snaking_shots_wave() -> None:
    assert isinstance(styled(style="wave"), WaveBullet)


def test_the_players_missiles_home_and_splash() -> None:
    missile = styled_bullet(
        Gun("fan", 1.0, speed=0.8, bullet="missile", homing=90.0, splash=2.0, splash_radius=0.1, size=(0.03, 0.07)),
        Entity(),
        0.0,
        0.8,
        hostile=False,
        depth=-0.02,
    )
    assert isinstance(missile, Missile)
    assert (missile.homing, missile.turn_rate) == (True, pytest.approx(math.pi / 2))
    assert (missile.splash_damage, missile.splash_radius, missile.hostile, missile.depth) == (2.0, 0.1, False, -0.02)
