"""The "cycle" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Cycle(Condition):
    """start <= the enemy's age % period < end."""

    period: float
    start: float
    end: float

    def holds(self, body: Body, target: Entity) -> bool:
        return self.start <= body.age % self.period < self.end
