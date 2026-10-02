"""The "swoop" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Swoop(Motion):
    """Up and down: vy = amplitude * cos(age * rate)."""

    amplitude: float = 0.0
    rate: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        body.vy = self.amplitude * math.cos(body.age * self.rate)
