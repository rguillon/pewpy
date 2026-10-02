"""The player's missile."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets.bullet import Bullet


@dataclass(eq=False)
class Missile(Bullet):
    """The player's missile: maybe homing (turning towards the nearest target, at most `turn_rate` radians per
    second), maybe blowing up enemies within `splash_radius` too (`splash_damage` each).
    """

    drawing: ClassVar[str] = "missile"  # its model: models/missile.json
    width: float = 0.03
    height: float = 0.07
    homing: bool = False
    turn_rate: float = 0.0
    splash_damage: float = 0.0
    splash_radius: float = 0.0

    def steer(self, dt: float, targets: Sequence[Entity]) -> None:
        """Turn toward the nearest target, at most `turn_rate`; fly straight if there is none."""
        if not self.homing or not targets:
            return
        target = min(targets, key=lambda entity: math.hypot(entity.x - self.x, entity.y - self.y))
        speed = math.hypot(self.vx, self.vy)
        heading = math.atan2(self.vy, self.vx)
        wanted = math.atan2(target.y - self.y, target.x - self.x)
        difference = (wanted - heading + math.pi) % (2 * math.pi) - math.pi
        heading += max(-self.turn_rate * dt, min(self.turn_rate * dt, difference))
        self.vx, self.vy = math.cos(heading) * speed, math.sin(heading) * speed
