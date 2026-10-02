"""What every motion is."""

from abc import ABC, abstractmethod

from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity


class Motion(ABC):
    """How an enemy moves each frame, in one of its states.

    It sets the body's speed (or its place), then the body moves with its speed.
    """

    @abstractmethod
    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:
        """Move `body` for a frame of `dt` seconds.

        `target` is the player, `scroll_speed` how fast the scenery under it scrolls.
        """
