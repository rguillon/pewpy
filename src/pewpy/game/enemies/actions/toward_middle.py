"""The "toward_middle" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class TowardMiddle(Action):
    """Sideways at `speed`, towards the middle of the screen."""

    speed: float = 0.0

    def do(self, body: Body, target: Entity) -> list[Entity]:
        """Move sideways towards the middle of the screen at `speed`."""
        body.vx = self.speed if body.x <= 0 else -self.speed
        return []
