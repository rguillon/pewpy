"""The "erratic" motion."""

import math
from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def erratic(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """A new sideways drift every `every` seconds: speed * sin(turns * a + x * b)."""
    enemy.turn_timer -= dt
    if enemy.turn_timer <= 0:
        enemy.turn_timer = motion.every
        enemy.turns += 1
        enemy.vx = motion.speed * math.sin(enemy.turns * motion.a + enemy.x * motion.b)
