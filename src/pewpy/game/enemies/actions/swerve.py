"""The "swerve" action: sideways towards the player's column, `gain` times the gap, at most `limit` either way."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def swerve(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    enemy.vx = max(-action.limit, min(action.limit, (target.x - enemy.x) * action.gain))
    return []
