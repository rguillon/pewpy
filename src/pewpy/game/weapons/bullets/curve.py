"""The "curve" style's shot."""

import math
from dataclasses import dataclass

from pewpy.game.weapons.bullets.bullet import Bullet

CURVE_TIME = 1.5  # "curve" shots bend this long, then fly straight


@dataclass(eq=False)
class CurveBullet(Bullet):
    """A shot whose path bends by `turn_rate` degrees per second (positive: counterclockwise) for `bend_time`
    seconds, then goes straight on (it would fly in circles).
    """

    turn_rate: float = 0.0
    bend_time: float = CURVE_TIME

    def move(self, dt: float) -> None:
        bending = min(dt, max(self.bend_time, 0.0))
        self.bend_time -= dt
        angle = math.radians(self.turn_rate * bending)
        cos, sin = math.cos(angle), math.sin(angle)
        self.vx, self.vy = self.vx * cos - self.vy * sin, self.vx * sin + self.vy * cos
        super().move(dt)
