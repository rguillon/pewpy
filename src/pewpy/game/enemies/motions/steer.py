"""The "steer" motion."""

import math
from typing import TYPE_CHECKING

from pewpy import config
from pewpy.game.enemies.motions.forward import forward
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def steer(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Turn towards the player (or straight down), at most `rate`, flying at `speed`."""
    rate = motion.rate / config.WIDTH_SCALE if motion.widen else motion.rate
    if not motion.inside or abs(enemy.x) <= HALF_WIDTH + enemy.width / 2:
        if motion.goal == "down":
            difference = (-math.pi / 2 - enemy.heading + math.pi) % (2 * math.pi) - math.pi
        else:
            wanted = math.atan2(target.y - enemy.y, target.x - enemy.x)
            difference = (wanted - enemy.heading + math.pi) % (2 * math.pi) - math.pi
        enemy.heading += max(-rate * dt, min(rate * dt, difference))
    forward(enemy, motion, dt, target, scroll_speed)
