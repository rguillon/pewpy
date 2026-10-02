"""The "accelerate" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def accelerate(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Speed up by `rate` per second until `top`."""
    speed = math.hypot(enemy.vx, enemy.vy)
    if 0 < speed < motion.top:
        faster = min(motion.top, speed + motion.rate * dt) / speed
        enemy.vx, enemy.vy = enemy.vx * faster, enemy.vy * faster
