"""What every exit condition is."""

from abc import ABC, abstractmethod
from typing import ClassVar

from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


class Condition(ABC):
    """Something that must hold for an enemy to leave its state that way (see Exit)."""

    after_guns: ClassVar[bool] = False  # checked after the state's guns have fired (else before the enemy moves)

    @abstractmethod
    def holds(self, body: Body, target: Entity) -> bool:
        """Whether it holds for `body` (`target` is the player)."""
