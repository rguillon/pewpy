"""The "velocity" action: set the enemy's speeds (each one left as it is if not given)."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def velocity(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    enemy.vx = enemy.vx if action.vx is None else action.vx
    enemy.vy = enemy.vy if action.vy is None else action.vy
    return []
