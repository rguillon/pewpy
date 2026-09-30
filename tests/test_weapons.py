import math

import pytest

from pewpy import config
from pewpy.enemies import Drone, Enemy, ShieldCarrier, Swarmer
from pewpy.entities import Entity, Pickup
from pewpy.level import Level, Wave
from pewpy.player import DEFAULT_SHIP, SHIPS
from pewpy.weapons import (
    BULLET_FIRE_RATE,
    LASER_LEVELS,
    MISSILE_FIRE_RATE,
    Arsenal,
    Missile,
)
from pewpy.world import Controls, World

DT = 1 / 60
SHIP = Entity(x=0.0, y=-0.75, width=0.12, height=0.12)
QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))


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


def test_upgrade_stops_at_level_3():
    arsenal = Arsenal()
    assert arsenal.upgrade("laser")
    assert arsenal.upgrade("laser")
    assert not arsenal.upgrade("laser")
    assert arsenal.levels["laser"] == 3


@pytest.mark.parametrize(("level", "count", "damage"), [(1, 1, 1.0), (2, 3, 0.8), (3, 5, 0.8)])
def test_bullet_patterns(level, count, damage):
    shots = arsenal_with("bullets", level).fire(DT, True, SHIP)
    assert len(shots) == count
    assert all(shot.damage == damage and shot.vy > 0 for shot in shots)
    angles = sorted(round(math.degrees(math.atan2(shot.vx, shot.vy))) for shot in shots)
    assert angles == {1: [0], 2: [-12, 0, 12], 3: [-24, -12, 0, 12, 24]}[level]


def test_fire_rates():
    assert len(shots_over(arsenal_with("bullets", 1), 2.0)) == pytest.approx(2 * BULLET_FIRE_RATE, abs=1)
    assert len(shots_over(arsenal_with("missiles", 1), 2.0)) == pytest.approx(2 * MISSILE_FIRE_RATE, abs=1)


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


# --- in the world ---


def make_world(weapon: str = "bullets", level: int = 1) -> World:
    return World(QUIET_LEVEL, seed=0, arsenal=arsenal_with(weapon, level))


def still_enemy(kind: type[Enemy] = Drone, **fields) -> Enemy:
    return kind(vy=0.0, fire_cooldown=1000.0, **fields)


def test_laser_hits_only_the_first_enemy_until_level_3():
    world = make_world("laser", 1)
    near, far = still_enemy(x=0.0, y=0.0), still_enemy(x=0.0, y=0.5)
    world.enemies += [near, far]
    world.update(0.25, Controls(fire=True))
    assert near.health == pytest.approx(3.0 - 8.0 * 0.25)
    assert far.health == 3.0
    assert world.laser is not None
    assert world.laser.top == pytest.approx(near.y - near.height / 2)


def test_piercing_laser_hits_every_enemy_in_the_beam():
    world = make_world("laser", 3)
    enemies = [still_enemy(x=0.03, y=0.0), still_enemy(x=0.0, y=0.5), still_enemy(x=0.5, y=0.5)]
    world.enemies += enemies
    world.update(0.1, Controls(fire=True))
    assert [enemy.health for enemy in enemies] == pytest.approx([3.0 - 1.8, 3.0 - 1.8, 3.0])
    assert world.laser is not None
    assert world.laser.top == config.PLAY_HEIGHT / 2


def test_laser_reaches_the_top_of_the_screen_but_not_beyond():
    # The tilted camera shows more than the play area at the top: the beam goes up to the screen's edge.
    world = World(QUIET_LEVEL, seed=0, arsenal=arsenal_with("laser", 3), view_top=1.6)
    in_the_band, above_the_screen = still_enemy(x=0.0, y=1.3), still_enemy(x=0.0, y=1.8)
    world.enemies += [in_the_band, above_the_screen]
    world.update(0.1, Controls(fire=True))
    assert world.laser is not None
    assert world.laser.top == 1.6
    assert in_the_band.health < 3.0
    assert above_the_screen.health == 3.0


def test_laser_kill_scores_and_beam_goes_away_when_not_firing():
    world = make_world("laser", 3)
    enemy = still_enemy(x=0.0, y=0.0)
    world.enemies.append(enemy)
    for _ in range(round(0.2 / DT)):
        world.update(DT, Controls(fire=True))
    assert not enemy.alive
    assert world.score == 100
    world.update(DT, Controls())
    assert world.laser is None


def test_shielded_enemy_stops_the_laser_without_damage():
    world = make_world("laser", 1)
    carrier = still_enemy(ShieldCarrier, x=0.0, y=0.0)
    world.enemies.append(carrier)
    world.update(0.1, Controls(fire=True))
    assert carrier.health == 10.0


def test_missile_explosion_damages_neighbors():
    world = make_world()
    target, neighbor, bystander = still_enemy(x=0.0, y=0.3), still_enemy(x=0.08, y=0.3), still_enemy(x=0.5, y=0.3)
    world.enemies += [target, neighbor, bystander]
    world.player_bullets.append(Missile(x=0.0, y=0.3, damage=3.0, splash_damage=1.5))
    world.update(DT, Controls())
    assert target.health == 0.0
    assert neighbor.health == 1.5
    assert bystander.health == 3.0


def test_destroyed_enemies_can_drop_pickups(monkeypatch):
    monkeypatch.setattr(Drone, "drop_chance", 1.0)
    world = make_world("laser", 3)
    enemy = still_enemy(x=0.0, y=0.0, health=0.1)
    world.enemies.append(enemy)
    world.update(DT, Controls(fire=True))
    assert len(world.pickups) == 1
    assert world.pickups[0].kind in {"bullets", "laser", "missiles", "repair"}
    assert (world.pickups[0].x, world.pickups[0].y) == pytest.approx((0.0, 0.0), abs=0.01)


def test_enemies_without_drops_never_drop():
    world = make_world("laser", 3)
    for y in (0.0, 0.2, 0.4, 0.6):
        world.enemies.append(still_enemy(Swarmer, x=0.0, y=y, health=0.1))  # Swarmers have no drops
    world.update(DT, Controls(fire=True))
    assert world.score == 4 * 50
    assert world.pickups == []


def test_upgrade_capsule_raises_that_weapon_and_keeps_the_selection():
    world = make_world("bullets", 1)
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="missiles"))
    world.update(DT, Controls())
    assert world.arsenal.levels["missiles"] == 2
    assert world.arsenal.selected == "bullets"
    assert world.pickups == []


def test_upgrade_at_max_level_gives_points():
    world = make_world("laser", 3)
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="laser"))
    world.update(DT, Controls())
    assert world.score == config.MAX_LEVEL_UPGRADE_POINTS


def test_repair_restores_health_up_to_the_maximum():
    world = make_world()
    world.player.health = 2.0
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="repair"))
    world.update(DT, Controls())
    assert world.player.health == 4.0
    world.pickups.append(Pickup(x=world.player.x, y=world.player.y, kind="repair"))
    world.update(DT, Controls())
    assert world.player.health == SHIPS[DEFAULT_SHIP].health


def test_pickups_drift_down_and_leave_the_screen():
    world = make_world()
    pickup = Pickup(x=0.6, y=-0.9)
    world.pickups.append(pickup)
    run_seconds = 2.0
    for _ in range(round(run_seconds / DT)):
        world.update(DT, Controls())
    assert world.pickups == []


def test_weapon_levels_survive_losing_a_life():
    world = make_world("missiles", 3)
    world.player.health = 0.0
    world.update(DT, Controls())
    assert world.lives == config.PLAYER_LIVES - 1
    assert world.arsenal.selected == "missiles"
    assert world.arsenal.levels["missiles"] == 3
