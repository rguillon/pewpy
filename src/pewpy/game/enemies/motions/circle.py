"""The "circle" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def circle(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Round in a small circle while coming down."""
    angle = enemy.age * motion.turn
    spin = motion.radius * motion.turn
    enemy.vx, enemy.vy = -spin * math.sin(angle), -motion.descent + spin * math.cos(angle)
