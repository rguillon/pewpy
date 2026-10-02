"""The "zigzag" motion."""

from typing import TYPE_CHECKING

from pewpy.game.enemies.motions.bounce import bounce
from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def zigzag(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Sideways at `speed`, first towards the player, turning back every `every` seconds and at the edges."""
    enemy.turn_timer -= dt
    if enemy.vx == 0:
        enemy.vx = motion.speed if target.x > enemy.x else -motion.speed
    bounce(enemy, motion, dt, target, scroll_speed)
    if enemy.turn_timer > 0:
        return
    enemy.turn_timer = motion.every
    enemy.vx = -enemy.vx
