"""The "volleys" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Volleys(Condition):
    """This many volleys fired in the state (checked after the guns)."""

    after_guns = True
    count: int

    def holds(self, body: Body, target: Entity) -> bool:
        return sum(gun.volleys for gun in body.guns) >= self.count
