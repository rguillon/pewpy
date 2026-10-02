"""The "to_bottom" action: just below the bottom of the screen."""

from typing import TYPE_CHECKING

from pewpy.game.enemies.screen import BOTTOM
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def to_bottom(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    enemy.y = BOTTOM - enemy.height
    return []
