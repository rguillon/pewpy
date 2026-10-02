"""The "aligned" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Aligned(Condition):
    """Within this of the player's column."""

    within: float

    def holds(self, body: Body, target: Entity) -> bool:
        return abs(target.x - body.x) <= self.within
