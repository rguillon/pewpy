import itertools
import math

import pytest

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets import Missile
from pewpy.game.weapons.guns import Gun
from pewpy.game.weapons.player.arsenal import LETTERS, LEVELS, MAX_LEVEL, WEAPONS, Arsenal

DT = 1 / 60
SHIP = Entity(x=0.0, y=-0.75, width=0.12, height=0.12)


def shots_over(arsenal: Arsenal, seconds: float) -> list:
    shots = []
    for _ in range(round(seconds / DT)):
        shots += arsenal.fire(DT, firing=True, ship=SHIP)
    return shots


def arsenal_with(weapon: str, level: int) -> Arsenal:
    arsenal = Arsenal(selected=weapon)
    arsenal.levels[weapon] = level
    return arsenal


def per_volley(gun: Gun) -> int:
    """Shots in one volley of a bullets or missiles gun."""
    item = gun.sequence[0] if gun.sequence else gun
    return len(item.origins) * len(item.angles or (0,))


def test_the_weapons_and_their_levels_are_read() -> None:
    assert WEAPONS == ("bullets", "laser", "missiles")
    assert set(LETTERS) == set(WEAPONS)
    assert {len(levels) for levels in LEVELS.values()} == {MAX_LEVEL}


def test_all_weapons_available_from_the_start_at_level_1() -> None:
    arsenal = Arsenal()
    assert arsenal.selected == WEAPONS[0]
    assert arsenal.levels == dict.fromkeys(WEAPONS, 1)


def test_switch_cycles_through_the_weapons() -> None:
    arsenal = Arsenal()
    selected = []
    for _ in range(len(WEAPONS) + 1):
        arsenal.switch()
        selected.append(arsenal.selected)
    assert selected == [*WEAPONS[1:], WEAPONS[0], WEAPONS[1]]


def test_upgrade_stops_at_the_top_level() -> None:
    arsenal = Arsenal()
    for _ in range(MAX_LEVEL - 1):
        assert arsenal.upgrade("laser")
    assert not arsenal.upgrade("laser")
    assert arsenal.levels["laser"] == MAX_LEVEL


@pytest.mark.parametrize("level", range(1, MAX_LEVEL + 1))
def test_bullets_fire_their_pattern_up_from_the_nose(level: int) -> None:
    gun = LEVELS["bullets"][level - 1]
    shots = arsenal_with("bullets", level).fire(DT, firing=True, ship=SHIP)
    assert sorted(round(math.degrees(math.atan2(shot.vx, shot.vy))) for shot in shots) == sorted(gun.angles)
    assert all(shot.damage == gun.damage and shot.vy > 0 and not shot.hostile for shot in shots)
    assert all(shot.y == pytest.approx(SHIP.y + SHIP.height / 2) for shot in shots)


@pytest.mark.parametrize(
    ("weapon", "level"), [("bullets", 1), ("bullets", MAX_LEVEL), ("missiles", 1), ("missiles", MAX_LEVEL)]
)
def test_fire_rates(weapon: str, level: int) -> None:
    gun = LEVELS[weapon][level - 1]
    volleys = len(shots_over(arsenal_with(weapon, level), 2.0)) / per_volley(gun)
    assert volleys == pytest.approx(2.0 / gun.interval, abs=1)


def test_every_level_is_stronger_than_the_one_before() -> None:
    for before, after in itertools.pairwise(LEVELS["laser"]):
        assert after.width >= before.width
        assert (after.damage or 0) > (before.damage or 0)
    for weapon in ("bullets", "missiles"):
        power = [
            per_volley(gun) * ((gun.sequence[0] if gun.sequence else gun).damage or 0) / gun.interval
            for gun in LEVELS[weapon]
        ]
        assert power == sorted(power)


def test_laser_fires_no_projectiles() -> None:
    arsenal = arsenal_with("laser", 2)
    assert shots_over(arsenal, 1.0) == []
    assert arsenal.laser(firing=True) == LEVELS["laser"][1]
    assert arsenal.laser(firing=False) is None


def test_missiles_alternate_sides_then_fire_in_pairs() -> None:
    level_1 = shots_over(arsenal_with("missiles", 1), 1.0)
    assert all(isinstance(shot, Missile) and not shot.homing for shot in level_1)
    assert level_1[0].x > SHIP.x > level_1[1].x
    first_salvo = arsenal_with("missiles", 3).fire(DT, firing=True, ship=SHIP)
    assert len(first_salvo) == 2
    assert all(isinstance(shot, Missile) and shot.homing and shot.splash_damage > 0 for shot in first_salvo)


def test_the_weapons_share_their_wait_and_it_doesnt_build_up_while_not_firing() -> None:
    arsenal = arsenal_with("missiles", 1)
    assert arsenal.fire(DT, firing=True, ship=SHIP)
    arsenal.switch()
    arsenal.switch()  # bullets
    assert arsenal.fire(DT, firing=True, ship=SHIP) == []  # still waiting after the missile
    for _ in range(120):
        arsenal.fire(DT, firing=False, ship=SHIP)
    assert arsenal.cooldown == 0.0


def test_a_full_arsenal_has_every_weapon_at_its_top_level() -> None:
    arsenal = Arsenal.full()
    assert arsenal.levels == dict.fromkeys(WEAPONS, MAX_LEVEL)
    assert not arsenal.upgrade(WEAPONS[0])
