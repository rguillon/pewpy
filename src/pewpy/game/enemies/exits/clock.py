"""The "clock" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Clock(Condition):
    """This many seconds in the state."""

    seconds: float

    def holds(self, body: Body, target: Entity) -> bool:
        return body.clock >= self.seconds
