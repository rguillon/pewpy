"""The "aim" action: fly straight at the player, at `speed`."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def aim(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    dx, dy = target.x - enemy.x, target.y - enemy.y
    distance = math.hypot(dx, dy) or 1.0
    enemy.vx, enemy.vy = dx / distance * action.speed, dy / distance * action.speed
    return []
