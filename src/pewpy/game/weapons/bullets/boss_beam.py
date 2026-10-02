"""A boss's laser beam (a "laser" gun), following the boss."""

from dataclasses import dataclass

from pewpy.game.entities import Entity
from pewpy.game.weapons.bullets.beam import BEAM_BOTTOM
from pewpy.game.weapons.bullets.bullet import Bullet


@dataclass(eq=False)
class BossBeam(Bullet):
    """A laser beam (or its harmless warning) from under `source` straight down past the bottom of the screen.

    It follows its source; it goes when its time is up or its source is destroyed.
    """

    source: Entity | None = None
    offset_x: float = 0.0

    def move(self, dt: float) -> None:
        """Follow the source (and go with it), then count down the beam's life."""
        if self.source is not None:
            if not self.source.alive:
                self.alive = False
            top = self.source.y - self.source.height / 2
            self.x = self.source.x + self.offset_x
            self.y, self.height = (top + BEAM_BOTTOM) / 2, max(top - BEAM_BOTTOM, 0.0)
        super().move(dt)
