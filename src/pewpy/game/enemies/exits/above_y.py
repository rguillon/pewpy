"""The "above_y" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class AboveY(Condition):
    """The enemy is that high."""

    y: float

    def holds(self, body: Body, target: Entity) -> bool:
        """Tell whether the enemy is at or above `y`."""
        return body.y >= self.y
