"""The "die" action: the enemy goes, without blowing up nor scoring (its time is up)."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def die(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    enemy.alive = False
    return []
