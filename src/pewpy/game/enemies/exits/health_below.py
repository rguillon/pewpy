"""The "health_below" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class HealthBelow(Condition):
    """Health below this share of the full health."""

    share: float

    def holds(self, body: Body, target: Entity) -> bool:
        return body.health < self.share * body.full_health
