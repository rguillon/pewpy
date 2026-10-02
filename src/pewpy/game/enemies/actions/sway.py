"""The "sway" action."""

import math
from dataclasses import dataclass

from pewpy import config
from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Sway(Action):
    """Sideways at `speed` (widened with the screen), on the way it was going (right if still)."""

    speed: float = 0.0

    def do(self, body: Body, target: Entity) -> list[Entity]:
        body.vx = math.copysign(self.speed * config.WIDTH_SCALE, body.vx or 1.0)
        return []
