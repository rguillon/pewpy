import math

import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.player.arsenal import (
    BULLET_FIRE_RATE,
    BULLET_FIRE_RATES,
    BULLET_PATTERNS,
    LASER_LEVELS,
    MAX_LEVEL,
    MISSILE_FIRE_RATE,
    MISSILE_LEVELS,
    Arsenal,
    Missile,
)

DT = 1 / 60
SHIP = Entity(x=0.0, y=-0.75, width=0.12, height=0.12)


def shots_over(arsenal: Arsenal, seconds: float) -> list:
    shots = []
    for _ in range(round(seconds / DT)):
        shots += arsenal.fire(DT, True, SHIP)
    return shots


def arsenal_with(weapon: str, level: int) -> Arsenal:
    arsenal = Arsenal(selected=weapon)
    arsenal.levels[weapon] = level
    return arsenal


def test_all_weapons_available_from_the_start_at_level_1():
    arsenal = Arsenal()
    assert arsenal.selected == "bullets"
    assert arsenal.levels == {"bullets": 1, "laser": 1, "missiles": 1}


def test_switch_cycles_through_the_three_weapons():
    arsenal = Arsenal()
    selected = []
    for _ in range(4):
        arsenal.switch()
        selected.append(arsenal.selected)
    assert selected == ["laser", "missiles", "bullets", "laser"]


def test_upgrade_stops_at_level_5():
    arsenal = Arsenal()
    for _ in range(4):
        assert arsenal.upgrade("laser")
    assert not arsenal.upgrade("laser")
    assert arsenal.levels["laser"] == 5


@pytest.mark.parametrize(
    ("level", "count", "damage"), [(1, 1, 1.0), (2, 3, 0.8), (3, 5, 0.8), (4, 5, 1.0), (5, 7, 1.0)]
)
def test_bullet_patterns(level, count, damage):
    shots = arsenal_with("bullets", level).fire(DT, True, SHIP)
    assert len(shots) == count
    assert all(shot.damage == damage and shot.vy > 0 for shot in shots)
    angles = sorted(round(math.degrees(math.atan2(shot.vx, shot.vy))) for shot in shots)
    expected = {
        1: [0],
        2: [-12, 0, 12],
        3: [-24, -12, 0, 12, 24],
        4: [-24, -12, 0, 12, 24],
        5: [-30, -20, -10, 0, 10, 20, 30],
    }
    assert angles == expected[level]


def test_fire_rates():
    assert len(shots_over(arsenal_with("bullets", 1), 2.0)) == pytest.approx(2 * BULLET_FIRE_RATE, abs=1)
    assert len(shots_over(arsenal_with("missiles", 1), 2.0)) == pytest.approx(2 * MISSILE_FIRE_RATE, abs=1)


def test_the_top_levels_fire_faster():
    bullets_5 = len(shots_over(arsenal_with("bullets", 5), 2.0)) / 7  # volleys of 7
    assert bullets_5 == pytest.approx(2 * BULLET_FIRE_RATES[5], abs=1) and BULLET_FIRE_RATES[5] > BULLET_FIRE_RATE
    missiles_5 = len(shots_over(arsenal_with("missiles", 5), 2.0)) / 2  # pairs
    assert missiles_5 == pytest.approx(2 * MISSILE_LEVELS[5].fire_rate, abs=1)
    assert MISSILE_LEVELS[5].fire_rate > MISSILE_FIRE_RATE


def test_every_level_is_stronger_than_the_one_before():
    for level in range(2, MAX_LEVEL + 1):
        before, after = LASER_LEVELS[level - 1], LASER_LEVELS[level]
        assert after.width >= before.width and after.damage_per_second > before.damage_per_second
        missile, previous = MISSILE_LEVELS[level], MISSILE_LEVELS[level - 1]
        assert (
            missile.damage * missile.per_shot * missile.fire_rate
            >= previous.damage * previous.per_shot * previous.fire_rate
        )
        angles, damage = BULLET_PATTERNS[level]
        old_angles, old_damage = BULLET_PATTERNS[level - 1]
        assert (
            len(angles) * damage * BULLET_FIRE_RATES[level]
            > len(old_angles) * old_damage * BULLET_FIRE_RATES[level - 1]
        )


def test_laser_fires_no_projectiles():
    arsenal = arsenal_with("laser", 2)
    assert shots_over(arsenal, 1.0) == []
    assert arsenal.laser(firing=True) == LASER_LEVELS[2]
    assert arsenal.laser(firing=False) is None


def test_missiles_alternate_sides_then_fire_in_pairs():
    level_1 = shots_over(arsenal_with("missiles", 1), 1.0)
    assert all(isinstance(shot, Missile) and not shot.homing for shot in level_1)
    assert level_1[0].x > SHIP.x > level_1[1].x
    first_salvo = arsenal_with("missiles", 3).fire(DT, True, SHIP)
    assert len(first_salvo) == 2
    assert all(isinstance(shot, Missile) and shot.homing and shot.splash_damage == 1.5 for shot in first_salvo)


def test_homing_missile_turns_toward_the_nearest_target_at_limited_rate():
    missile = Missile(x=0.0, y=0.0, vy=1.6, homing=True)
    far, near = Entity(x=-0.5, y=0.8), Entity(x=0.4, y=0.0)
    missile.steer(0.1, [far, near])
    assert missile.vx > 0  # turning right, toward the nearest
    assert math.hypot(missile.vx, missile.vy) == pytest.approx(1.6)
    assert math.degrees(math.atan2(missile.vx, missile.vy)) == pytest.approx(18.0)  # 180 deg/s for 0.1 s


def test_straight_missile_ignores_targets():
    missile = Missile(x=0.0, y=0.0, vy=1.6, homing=False)
    missile.steer(0.1, [Entity(x=0.4, y=0.0)])
    assert (missile.vx, missile.vy) == (0.0, 1.6)
