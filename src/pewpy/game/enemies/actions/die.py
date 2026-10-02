"""The "die" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Die(Action):
    """The enemy goes, without blowing up nor scoring (its time is up)."""

    def do(self, body: Body, target: Entity) -> list[Entity]:
        """Die (without exploding: it's gone)."""
        body.alive = False
        return []
