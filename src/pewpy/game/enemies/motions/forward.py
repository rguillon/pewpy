"""The "forward" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Forward(Motion):
    """Straight on the way it's heading, at `speed`."""

    speed: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        body.vx, body.vy = math.cos(body.heading) * self.speed, math.sin(body.heading) * self.speed
