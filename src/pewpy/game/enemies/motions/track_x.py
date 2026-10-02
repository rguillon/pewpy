"""The "track_x" motion."""

import math
from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class TrackX(Motion):
    """Sideways towards the player's column, at `speed`; still once within `dead_zone` of it."""

    speed: float = 0.0
    dead_zone: float = 0.02

    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Move sideways towards the target at `speed`, still within `dead_zone` of it."""
        gap = target.x - body.x
        body.vx = math.copysign(self.speed, gap) if abs(gap) > self.dead_zone else 0.0
