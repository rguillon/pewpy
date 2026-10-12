import math

import pytest

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns.gun import Gun
from pewpy.game.weapons.guns.launch import PROJECTILES, launch
from pewpy.game.weapons.guns.patterns import fire
from tests.game.weapons.guns.shooting import shooter


@pytest.mark.parametrize(
    ("projectile", "kind", "speed"),
    [("rocket", "rocket", 0.25), ("missile", "homing_missile", 0.0), ("cluster", "cluster_bomb", 0.3)],
)
def test_guns_can_launch_projectiles_the_shots_way(projectile: str, kind: str, speed: float) -> None:
    assert PROJECTILES[projectile] == (kind, speed)
    gun = Gun("fan", interval=1.0, speed=0.0, count=3, spread=20, projectile=projectile)
    shots = fire(gun, shooter())
    assert [shot.kind for shot in shots if isinstance(shot, Enemy)] == [kind] * 3
    assert [math.hypot(shot.vx, shot.vy) for shot in shots] == pytest.approx([speed] * 3)
    first = shots[0]
    assert isinstance(first, Enemy)
    assert math.degrees(first.heading) == pytest.approx(-90 - 20)


def test_guns_can_spawn_enemies_as_they_are_or_on_their_way() -> None:
    plain = fire(Gun("fan", 1, speed=0.0, spawn="rocket"), shooter())[0]
    assert (plain.vx, plain.vy) == (0.0, -0.25)  # a rocket's own speed
    pair = fire(
        Gun("fan", 1, speed=0.0, spawn="dart", spawn_velocity=(0.3, -0.5), origins=((-0.1, 0), (0.1, 0))), shooter()
    )
    assert [(dart.vx, dart.vy) for dart in pair] == [(-0.3, -0.5), (0.3, -0.5)]  # mirrored on the left
    middle = fire(Gun("fan", 1, speed=0.0, spawn="dart", spawn_velocity=(0.3, -0.5)), shooter())[0]
    assert middle.vx == 0.3
    upwards = fire(Gun("fan", 1, speed=0.0, spawn="homing_missile", spawn_heading=90.0), shooter())[0]
    assert isinstance(upwards, Enemy)
    assert upwards.heading == pytest.approx(math.pi / 2)


def test_a_shell_can_be_timed_to_burst_where_the_player_is() -> None:
    gun = Gun("aimed", 1, speed=0.0, spawn="cluster_bomb", spawn_speed=0.5, spawn_fuse=True)
    shell = fire(gun, shooter(Entity(x=0.0, y=0.5), Entity(x=0.0, y=-0.5)))[0]
    assert isinstance(shell, Enemy)
    assert shell.timer_override == pytest.approx(1.0 / 0.5)
    assert (shell.vx, shell.vy) == pytest.approx((0.0, -0.5))


def test_a_launched_enemy_is_made_at_the_muzzle() -> None:
    made = []

    def make(kind: str, x: float, y: float, heading: float | None, timer: float | None) -> Entity:
        made.append((kind, x, y, heading, timer))
        return Entity(x=x, y=y)

    aim = shooter()
    aim.make = make
    enemy = launch(Gun("fan", 1, speed=0.0, spawn="drone"), Entity(x=0.1, y=0.2), 0.0, 0.0, aim)
    assert made == [("drone", 0.1, 0.2, None, None)]
    assert (enemy.vx, enemy.vy) == (0.0, 0.0)  # it flies as it would on its own
