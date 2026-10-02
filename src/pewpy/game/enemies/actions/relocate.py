"""The "relocate" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Relocate(Action):
    """Somewhere else across the screen, `step` of it further (wrapping round), and `dy` up or down."""

    step: float = 0.0
    dy: float = 0.0

    def do(self, body: Body, target: Entity) -> list[Entity]:
        span = HALF_WIDTH - body.width
        body.x = ((body.x / span + 1) / 2 + self.step) % 1.0 * 2 * span - span
        body.y += self.dy
        return []
