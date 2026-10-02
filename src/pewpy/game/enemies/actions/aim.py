"""The "aim" action."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Aim(Action):
    """Fly straight at the player, at `speed`."""

    speed: float = 0.0

    def do(self, body: Body, target: Entity) -> list[Entity]:
        """Head straight for the target at `speed`."""
        dx, dy = target.x - body.x, target.y - body.y
        distance = math.hypot(dx, dy) or 1.0
        body.vx, body.vy = dx / distance * self.speed, dy / distance * self.speed
        return []
