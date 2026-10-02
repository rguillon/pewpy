"""The "patrol" motion."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def patrol(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Sideways at `speed`, towards the middle first (whenever it's standing still sideways)."""
    if enemy.vx == 0:
        enemy.vx = motion.speed if enemy.x <= 0 else -motion.speed
