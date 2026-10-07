import random

import pytest

from pewpy.game.enemies.enemy import Enemy
from pewpy.game.enemies.roster import ENEMY_TYPES, make_enemy
from pewpy.game.enemies.screen import HALF_WIDTH, TOP
from pewpy.game.entities import Entity

DT = 1 / 60
TARGET = Entity(x=0.0, y=-0.75)  # where the player starts
SCROLL = 0.2


def run(enemy: Enemy, seconds: float, target: Entity = TARGET) -> list[Entity]:
    created = []
    for _ in range(round(seconds / DT)):
        created += enemy.update(DT, target, SCROLL)
    return created


@pytest.mark.parametrize("kind", sorted(ENEMY_TYPES))
def test_every_enemy_type_enters_and_runs(kind: str) -> None:
    rng = random.Random(0)
    enemy = make_enemy(kind, x=5.0, y=0.5, side="right", rng=rng)
    if enemy.side_entry:
        assert enemy.x > HALF_WIDTH
    else:
        assert enemy.y > TOP
        assert abs(enemy.x) <= HALF_WIDTH - enemy.width / 2  # x=5.0 was clamped
    start = (enemy.x, enemy.y)
    run(enemy, 20.0)
    assert (enemy.x, enemy.y) != start


def test_side_entry_from_the_left_moves_right() -> None:
    enemy = make_enemy("mine_layer", x=0, y=0.3, side="left", rng=random.Random(0))
    assert enemy.x < -HALF_WIDTH
    assert enemy.y == 0.3
    run(enemy, 1.0)
    assert enemy.vx > 0


def test_only_ground_enemies_are_marked_as_on_the_ground() -> None:
    assert {kind for kind, enemy in ENEMY_TYPES.items() if enemy.ground} == {"turret", "flak_cannon"}
