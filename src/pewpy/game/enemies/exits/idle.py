"""The "idle" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Idle(Condition):
    """No gun is charging, firing a beam or in the middle of a volley."""

    def holds(self, body: Body, target: Entity) -> bool:
        """Tell whether none of the enemy's guns is busy."""
        return not any(gun.busy for gun in body.guns)
