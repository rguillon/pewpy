"""The "patrol" motion."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Patrol(Motion):
    """Sideways at `speed`, towards the middle first (whenever it's standing still sideways)."""

    speed: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Start moving sideways towards the middle if it isn't moving sideways."""
        if body.vx == 0:
            body.vx = self.speed if body.x <= 0 else -self.speed
