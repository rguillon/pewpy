"""The "timer" exit condition."""

from dataclasses import dataclass

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Timer(Condition):
    """The state's timer has run out."""

    def holds(self, body: Body, target: Entity) -> bool:
        return body.timer <= 0
