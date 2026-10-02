"""The "below_y" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class BelowY(Condition):
    """The enemy is that low."""

    y: float

    def holds(self, body: Body, target: Entity) -> bool:
        """Tell whether the enemy is at or below `y`."""
        return body.y <= self.y
