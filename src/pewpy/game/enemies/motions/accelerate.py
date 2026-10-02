"""The "accelerate" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Accelerate(Motion):
    """Speed up by `rate` per second until `top`."""

    rate: float = 0.0
    top: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Speed up along the way it's going, up to `top`."""
        speed = math.hypot(body.vx, body.vy)
        if 0 < speed < self.top:
            faster = min(self.top, speed + self.rate * dt) / speed
            body.vx, body.vy = body.vx * faster, body.vy * faster
