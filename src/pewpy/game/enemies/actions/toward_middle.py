"""The "toward_middle" action: sideways at `speed`, towards the middle of the screen."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def toward_middle(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    enemy.vx = action.speed if enemy.x <= 0 else -action.speed
    return []
