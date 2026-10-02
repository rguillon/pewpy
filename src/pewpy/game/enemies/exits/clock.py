"""The "clock" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Clock(Condition):
    """A number of seconds in the state."""

    seconds: float

    def holds(self, body: Body, target: Entity) -> bool:
        """Tell whether the enemy has been `seconds` in its state."""
        return body.clock >= self.seconds
