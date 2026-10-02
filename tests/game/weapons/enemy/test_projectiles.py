import itertools
import math

import pytest

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Bullet, Entity
from pewpy.game.weapons.enemy.projectiles import ClusterBomb, HomingMissile, Rocket

DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)  # where the player starts
SCROLL = 0.2


def run(enemy: Enemy, seconds: float, target: Entity = TARGET) -> list[Entity]:
    created = []
    for _ in range(round(seconds / DT)):
        created += enemy.update(DT, target, SCROLL)
    return created


def bullets(created: list[Entity]) -> list[Bullet]:
    return [entity for entity in created if isinstance(entity, Bullet)]


def test_rockets_fly_straight_and_speed_up_to_their_top_speed():
    rocket = Rocket(x=0.0, y=0.5)
    run(rocket, 0.1)
    assert rocket.vx == 0 and -Rocket.top_speed < rocket.vy < -0.25
    run(rocket, 3.0)
    assert rocket.vy == pytest.approx(-Rocket.top_speed)


def test_homing_missiles_turn_towards_the_player_until_their_fuel_runs_out():
    missile = HomingMissile(x=0.0, y=0.5, heading=math.pi / 2)  # launched upwards
    run(missile, 3.0, target=Entity(x=0.3, y=-0.75))
    assert missile.vy < 0  # turned round, towards the player below
    heading = missile.heading
    run(missile, 1.0, target=Entity(x=-0.5, y=0.9))  # out of fuel: no more turning
    assert missile.heading == pytest.approx(heading)
    assert math.hypot(missile.vx, missile.vy) == pytest.approx(HomingMissile.speed)


def test_cluster_bombs_burst_into_a_ring_of_shots_when_their_fuse_runs_out():
    bomb = ClusterBomb(x=0.0, y=0.5)
    assert bullets(run(bomb, 1.0)) == []
    shards = bullets(run(bomb, 0.3))
    assert len(shards) == ClusterBomb.shards
    assert not bomb.alive
    angles = sorted(math.degrees(math.atan2(shard.vy, shard.vx)) % 360 for shard in shards)
    assert [b - a for a, b in itertools.pairwise(angles)] == pytest.approx([45.0] * 7)  # evenly around
