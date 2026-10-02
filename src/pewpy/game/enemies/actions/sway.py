"""The "sway" action: sideways at `speed` (widened with the screen), on the way it was going (right if still)."""

import math
from typing import TYPE_CHECKING

from pewpy import config
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Action


def sway(enemy: "Enemy", action: "Action", target: Entity) -> list[Entity]:
    enemy.vx = math.copysign(action.speed * config.WIDTH_SCALE, enemy.vx or 1.0)
    return []
