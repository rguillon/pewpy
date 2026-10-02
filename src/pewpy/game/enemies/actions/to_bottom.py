"""The "to_bottom" action."""

from dataclasses import dataclass

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.enemies.screen import BOTTOM
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class ToBottom(Action):
    """Just below the bottom of the screen."""

    def do(self, body: Body, target: Entity) -> list[Entity]:
        body.y = BOTTOM - body.height
        return []
