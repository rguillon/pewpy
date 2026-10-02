"""The "steer" motion."""

import math
from dataclasses import dataclass

from pewpy import config
from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.forward import Forward
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Steer(Forward):
    """Turn towards the player (`goal` "target") or straight down ("down"), flying at `speed`.

    At most `rate` radians per second (narrowed with the screen if `widen`); `inside`: only once inside the screen.
    """

    rate: float = 0.0
    goal: str = "target"
    widen: bool = False
    inside: bool = False

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Turn towards the goal, then fly the way it's heading."""
        rate = self.rate / config.WIDTH_SCALE if self.widen else self.rate
        if not self.inside or abs(body.x) <= HALF_WIDTH + body.width / 2:
            if self.goal == "down":
                difference = (-math.pi / 2 - body.heading + math.pi) % (2 * math.pi) - math.pi
            else:
                wanted = math.atan2(target.y - body.y, target.x - body.x)
                difference = (wanted - body.heading + math.pi) % (2 * math.pi) - math.pi
            body.heading += max(-rate * dt, min(rate * dt, difference))
        super().apply(body, dt, target, scroll_speed)
