"""The "circle" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Circle(Motion):
    """Round in a small circle of `radius`, `turn` radians per second, while coming down at `descent`."""

    radius: float = 0.0
    turn: float = 0.0
    descent: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Fly around a circle while coming down."""
        angle = body.age * self.turn
        spin = self.radius * self.turn
        body.vx, body.vy = -spin * math.sin(angle), -self.descent + spin * math.cos(angle)
