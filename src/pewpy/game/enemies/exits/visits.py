"""The "visits" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Visits(Condition):
    """The state has been entered this many times (this time included)."""

    count: int

    def holds(self, body: Body, target: Entity) -> bool:
        return body.visits >= self.count
