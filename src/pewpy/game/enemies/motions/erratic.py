"""The "erratic" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Erratic(Motion):
    """A new sideways drift every `every` seconds: speed * sin(turns * a + x * b)."""

    speed: float = 0.0
    every: float = 0.0
    a: float = 0.0
    b: float = 0.0

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Change the sideways speed every `every` seconds, unpredictably."""
        body.turn_timer -= dt
        if body.turn_timer <= 0:
            body.turn_timer = self.every
            body.turns += 1
            body.vx = self.speed * math.sin(body.turns * self.a + body.x * self.b)
