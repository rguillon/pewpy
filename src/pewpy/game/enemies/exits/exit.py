"""A way out of an enemy's state."""

from dataclasses import dataclass

from pewpy.game.enemies.actions import Action
from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity


@dataclass(frozen=True)
class Exit:
    """A way out of a state, to the state named `to`, once all its conditions hold; `then` is done on the way."""

    to: str
    conditions: tuple[Condition, ...] = ()
    then: tuple[Action, ...] = ()
    go_on: bool = False  # the frame goes on in the new state (a boss's phases), instead of ending there...
    recheck: bool = False  # ...after checking the new state's exits too (otherwise one change per frame)

    @property
    def after_guns(self) -> bool:
        """Whether it's checked after the state's guns have fired (else before the enemy moves)."""
        return any(condition.after_guns for condition in self.conditions)

    def open(self, body: Body, target: Entity) -> bool:
        """Whether `body` can leave this way: all its conditions hold."""
        return all(condition.holds(body, target) for condition in self.conditions)
