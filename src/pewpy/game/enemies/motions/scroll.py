"""The "scroll" motion."""

from typing import TYPE_CHECKING

from pewpy.game.entities import Entity

if TYPE_CHECKING:
    from pewpy.game.enemies.enemy import Enemy
    from pewpy.game.enemies.spec import Motion


def scroll(enemy: "Enemy", motion: "Motion", dt: float, target: Entity, scroll_speed: float) -> None:
    """Fixed to the ground (or driving on it, `plus` faster)."""
    if motion.stop_x:
        enemy.vx = 0.0
    enemy.vy = -scroll_speed + motion.plus
