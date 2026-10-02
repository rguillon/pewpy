"""The "swerve" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Swerve(Action):
    """Sideways towards the player's column, `gain` times the gap, at most `limit` either way."""

    gain: float = 0.0
    limit: float = 0.0

    def do(self, body: Body, target: Entity) -> list[Entity]:
        body.vx = max(-self.limit, min(self.limit, (target.x - body.x) * self.gain))
        return []
