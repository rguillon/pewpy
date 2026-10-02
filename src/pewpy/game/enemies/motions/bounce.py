"""The "bounce" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def bounce(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Turn back at the screen's edges (a boss: its parts too, and kept inside)."""
    if motion.clamp:
        limit = HALF_WIDTH - enemy.spec.half_span
        if abs(enemy.x) >= limit and enemy.x * enemy.vx > 0:
            enemy.vx = -enemy.vx
            enemy.x = math.copysign(limit, enemy.x)
    elif abs(enemy.x) > HALF_WIDTH - enemy.width / 2 and enemy.x * enemy.vx > 0:
        enemy.vx = -enemy.vx
