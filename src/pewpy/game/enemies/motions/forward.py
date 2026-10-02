"""The "forward" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def forward(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Straight on the way it's heading, at `speed`."""
    enemy.vx, enemy.vy = math.cos(enemy.heading) * motion.speed, math.sin(enemy.heading) * motion.speed
