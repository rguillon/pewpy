"""What the AI sees of the world."""

import numpy as np
import pytest

from pewpy.ai import sensors
from pewpy.game.controls import Controls
from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Pickup
from pewpy.game.level import Level, Wave
from pewpy.game.weapons.bullets.bullet import Bullet
from pewpy.game.weapons.bullets.wave import WaveBullet
from pewpy.game.world import World

DT = 1 / 60
QUIET_LEVEL = Level(name="quiet", scroll_speed=0.2, waves=(Wave(time=1000.0),))
BOSS_LEVEL = Level(name="boss", scroll_speed=0.2, waves=(Wave(time=0.0, enemy="harvester"),))


def quiet_world() -> World:
    return World(QUIET_LEVEL, seed=0)


def still(kind: str = "drone", **fields: float) -> Enemy:
    enemy = Enemy.of_kind(kind)
    enemy.vy, enemy.fire_cooldown = 0.0, 1000.0
    for name, value in fields.items():
        setattr(enemy, name, value)
    return enemy


def shot(x: float, y: float, vy: float = -1.0, *, harmless: bool = False) -> Bullet:
    return Bullet(x=x, y=y, vy=vy, hostile=True, harmless=harmless)


def boss_world() -> World:
    world = World(BOSS_LEVEL, seed=0)
    for _ in range(6):
        world.update(DT, Controls())
    return world


def test_the_view_has_its_size_and_sees_nothing_in_an_empty_sky() -> None:
    world = quiet_world()
    view = sensors.sense(world)
    assert view.shape == (sensors.SIZE,)
    moves = len(sensors.MOVES)
    assert np.all(view[:moves] == 1.0)  # no hit coming, whatever the move
    assert view[sensors.SHOOTABLE] == 0.0
    assert tuple(view[sensors.AIM : sensors.AIM + 2]) == sensors.MOVES[0]  # nothing to aim at: stay put


def test_a_shot_coming_straight_at_the_ship_makes_staying_put_unsafe() -> None:
    world = quiet_world()
    player = world.player
    world.enemy_bullets.append(shot(player.x, player.y + 0.3))
    time, _room, score, _x, _y = sensors.radar(world, sensors._rows(world.enemy_bullets))
    assert time[0] < 1.0  # staying put gets hit
    assert score.max() > score[0]
    assert sensors.safest(score) != sensors.MOVES[0]


def test_far_away_threats_are_left_out() -> None:
    world = quiet_world()
    world.enemy_bullets.append(shot(world.player.x, world.player.y + 1.5, vy=0.0))
    time, room, *_ = sensors.radar(world, sensors._rows(world.enemy_bullets))
    assert np.all(time == 1.0)
    assert np.all(room == 1.0)


def test_dead_things_and_harmless_beams_are_not_seen_and_snaking_shots_are_as_wide_as_their_snaking() -> None:
    world = quiet_world()
    dead = still(x=0.0, y=0.5)
    dead.alive = False
    snaking = WaveBullet(x=0.1, y=0.5, hostile=True)
    world.enemies.append(dead)
    world.enemy_bullets += [snaking, shot(0.0, 0.4, harmless=True)]
    rows = sensors._rows([dead, snaking])
    assert len(rows) == 1
    assert rows[0, 4] == pytest.approx(snaking.width + 2 * snaking.amplitude)
    view = sensors.sense(world)
    shots = sensors.SAFEST + 4
    assert np.count_nonzero(view[shots : shots + 4 * sensors.NEAREST_SHOTS]) <= 4  # only the snaking one


def test_the_target_is_the_nearest_pickup_waiting_under_it_when_it_is_high() -> None:
    world = quiet_world()
    world.pickups += [Pickup(x=0.3, y=-0.2), Pickup(x=-0.5, y=0.8)]
    x, y = sensors.target(world) or (None, None)
    assert x == 0.3
    assert y == pytest.approx(-0.2 + world.pickups[0].vy * sensors.FIRST)
    world.pickups[:] = [Pickup(x=-0.5, y=0.8)]
    assert sensors.target(world) == (-0.5, sensors.CEILING)


def test_the_target_is_the_nearest_enemy_above_on_screen() -> None:
    world = quiet_world()
    assert sensors.target(world) is None
    world.enemies += [still(x=0.4, y=0.5), still(x=-0.1, y=0.6), still(x=0.0, y=world.player.y - 0.2)]
    assert sensors.target(world) == (-0.1, None)


def test_the_target_is_the_boss_part_nearest_across_while_the_core_is_armored_then_the_core() -> None:
    world = boss_world()
    boss = world.boss
    assert boss is not None
    world.player.x = boss.parts[0].x
    assert not boss.state.vulnerable
    assert sensors.target(world) == (boss.parts[0].x, None)
    for part in boss.parts:
        part.alive = False
    assert sensors.target(world) == (boss.x, None)


def test_the_view_sees_the_boss_the_targets_and_the_pickup() -> None:
    world = boss_world()
    world.pickups.append(Pickup(x=0.2, y=0.0))
    world.enemies.append(still(x=0.1, y=0.3))
    view = sensors.sense(world)
    boss = world.boss
    assert boss is not None
    assert view[sensors.SHOOTABLE - 4] == pytest.approx(boss.health_fraction)  # the boss's health
    assert view[sensors.SHOOTABLE - 7] == 1.0  # a pickup
    assert view[sensors.SHOOTABLE] == 1.0  # the drone can be hurt


def test_aiming_picks_the_safe_move_nearest_the_goal() -> None:
    score = np.zeros(len(sensors.MOVES))
    reach_x = np.array([x for x, _ in sensors.MOVES])
    reach_y = np.array([y for _, y in sensors.MOVES])
    assert sensors.aim(score, reach_x, reach_y, (1.0, 0.0)) == sensors.MOVES[1]  # right
    assert sensors.aim(score, reach_x, reach_y, (-1.0, None)) == sensors.MOVES[5]  # left, at home height
    score[5] = -1.0  # left is not safe
    assert sensors.aim(score, reach_x, reach_y, (-1.0, None)) != sensors.MOVES[5]


def test_the_repairs_tell_how_long_since_the_ship_fired() -> None:
    world = quiet_world()
    world.player.since_fired = 0.75
    assert sensors.repairs(world)[1] == pytest.approx(0.75 / world.player.ship.regeneration_delay)
    world.player.since_fired = 10.0
    assert sensors.repairs(world)[1] == 1.0


def test_the_lanes_count_what_is_above_the_ship() -> None:
    things = np.array([[0.0, 0.5, 0, 0, 0, 0]] * 6 + [[0.0, -0.9, 0, 0, 0, 0]])
    lanes = sensors._lanes(things, above=0.0)
    assert lanes.max() == 1.0  # at most 4 counted
    assert lanes.sum() == 1.0
    assert not sensors._lanes(sensors.NO_THREATS, 0.0).any()
