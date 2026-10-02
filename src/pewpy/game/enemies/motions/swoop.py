"""The "swoop" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def swoop(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Up and down: vy = amplitude * cos(age * rate)."""
    enemy.vy = motion.amplitude * math.cos(enemy.age * motion.rate)
