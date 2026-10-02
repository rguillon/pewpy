"""The "fire" action: one shot of its `gun` (while on screen, unless the gun fires off screen too)."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import fire as fire_gun

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def fire(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    gun = action.gun
    if gun is not None and (gun.off_screen == "fire" or enemy.on_screen):
        return fire_gun(gun, enemy.shooter(enemy, target))
    return []
