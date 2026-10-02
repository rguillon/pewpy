"""The "weave" motion."""

import math
from dataclasses import dataclass

from pewpy import config
from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Weave(Motion):
    """Snake from side to side around the column it came down.

    `amplitude` to each side (widened with the screen if `widen`), every `period` seconds.
    """

    amplitude: float = 0.0
    period: float = 1.0
    widen: bool = False

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Set the place along the snaking."""
        if body.base_x is None:
            body.base_x = body.x
        amplitude = self.amplitude * config.WIDTH_SCALE if self.widen else self.amplitude
        body.x = body.base_x + amplitude * math.sin(2 * math.pi * body.age / self.period)
