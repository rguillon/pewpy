"""The exit condition on `below_y`: the enemy is that low."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Exit


def below_y(enemy: "Enemy", way_out: "Exit", target: Entity) -> bool:
    return way_out.below_y is None or enemy.y <= way_out.below_y
