"""What every action is."""

from abc import ABC, abstractmethod

from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


class Action(ABC):
    """Something an enemy does once: when it appears (EnemySpec.start) or goes from a state to another (Exit.then)."""

    @abstractmethod
    def do(self, body: Body, target: Entity) -> list[Entity]:
        """Do it to `body` (`target` is the player); what it created (bullets, enemies)."""
