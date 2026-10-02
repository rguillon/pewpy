"""The "weave" motion."""

import math
from typing import TYPE_CHECKING

from pewpy import config
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def weave(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Snake from side to side around the column it came down."""
    if enemy.base_x is None:
        enemy.base_x = enemy.x
    amplitude = motion.amplitude * config.WIDTH_SCALE if motion.widen else motion.amplitude
    enemy.x = enemy.base_x + amplitude * math.sin(2 * math.pi * enemy.age / motion.period)
