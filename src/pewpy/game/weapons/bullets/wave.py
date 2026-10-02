"""The "wave" style's shot."""

import math
from dataclasses import dataclass

from pewpy.game.weapons.bullets.bullet import Bullet


@dataclass(eq=False)
class WaveBullet(Bullet):
    """A shot snaking from side to side across its line of flight."""

    amplitude: float = 0.06
    period: float = 0.7  # seconds for a full wave
    age: float = 0.0
    line_x: float | None = None  # where it would be flying straight
    line_y: float = 0.0

    def move(self, dt: float) -> None:
        if self.line_x is None:
            self.line_x, self.line_y = self.x, self.y
        self.age += dt
        self.line_x += self.vx * dt
        self.line_y += self.vy * dt
        speed = math.hypot(self.vx, self.vy) or 1.0
        offset = self.amplitude * math.sin(2 * math.pi * self.age / self.period)
        self.x, self.y = self.line_x - self.vy / speed * offset, self.line_y + self.vx / speed * offset
