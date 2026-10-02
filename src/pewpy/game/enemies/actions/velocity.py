"""The "velocity" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Velocity(Action):
    """Set the enemy's speeds (each one left as it is if None)."""

    vx: float | None = None
    vy: float | None = None

    def do(self, body: Body, target: Entity) -> list[Entity]:
        """Set the speed (each axis given; the others keep theirs)."""
        body.vx = body.vx if self.vx is None else self.vx
        body.vy = body.vy if self.vy is None else self.vy
        return []
