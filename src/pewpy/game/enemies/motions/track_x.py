"""The "track_x" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def track_x(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Sideways towards the player's column, at `speed`; still once within `dead_zone` of it."""
    gap = target.x - enemy.x
    enemy.vx = math.copysign(motion.speed, gap) if abs(gap) > motion.dead_zone else 0.0
