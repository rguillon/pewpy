"""The exit condition on `above_y`: the enemy is that high."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def above_y(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return way_out.above_y is None or enemy.y >= way_out.above_y
