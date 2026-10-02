"""The "accel" style's shot."""

import math
from dataclasses import dataclass

from pewpy.game.weapons.bullets.bullet import Bullet


@dataclass(eq=False)
class AccelBullet(Bullet):
    """A shot starting slow, speeding up by `rate` per second up to `top_speed`."""

    rate: float = 0.5
    top_speed: float = 1.0

    def move(self, dt: float) -> None:
        """Speed up towards `top_speed`, then move."""
        speed = math.hypot(self.vx, self.vy)
        if 0 < speed < self.top_speed:
            faster = min(self.top_speed, speed + self.rate * dt) / speed
            self.vx, self.vy = self.vx * faster, self.vy * faster
        super().move(dt)
