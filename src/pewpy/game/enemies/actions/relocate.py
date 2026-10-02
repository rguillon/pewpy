"""The "relocate" action: somewhere else across the screen, `step` of it further (wrapping round), and `dy` up or
down.
"""

from typing import TYPE_CHECKING

from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def relocate(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    span = HALF_WIDTH - enemy.width
    enemy.x = ((enemy.x / span + 1) / 2 + action.step) % 1.0 * 2 * span - span
    enemy.y += action.dy
    return []
