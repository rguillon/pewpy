"""The "bounce" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Bounce(Motion):
    """Turn back at the screen's edges (`clamp`: a boss, its parts too, and kept inside)."""

    clamp: bool = False

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        if self.clamp:
            limit = HALF_WIDTH - body.half_span
            if abs(body.x) >= limit and body.x * body.vx > 0:
                body.vx = -body.vx
                body.x = math.copysign(limit, body.x)
        elif abs(body.x) > HALF_WIDTH - body.width / 2 and body.x * body.vx > 0:
            body.vx = -body.vx
