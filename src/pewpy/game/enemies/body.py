"""What an enemy's motions, actions and exits act on (see motions/, actions/, exits/): its body, as they see it.
Enemy (enemy.py) is the one Body of the game; the behaviours only know this, so they don't depend on it. Independent
from rendering.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pewpy.game.enemies.screen import HALF_WIDTH, TOP
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import GunState, Shooter


@dataclass(eq=False)
class Body(Entity, ABC):
    health: float = 3.0
    age: float = 0.0
    heading: float = -math.pi / 2  # radians, the way a steering enemy flies
    timer: float = 0.0  # its state's countdown (see State.timer)
    clock: float = 0.0  # seconds in its state
    guns: list[GunState] = field(default_factory=list)  # its state's guns
    base_x: float | None = None  # weave
    turn_timer: float = 0.0  # zigzag, erratic
    turns: int = 0  # erratic

    @property
    def on_screen(self) -> bool:
        return self.y < TOP and abs(self.x) < HALF_WIDTH

    @property
    @abstractmethod
    def full_health(self) -> float:
        """Its health when it came in."""

    @property
    @abstractmethod
    def half_span(self) -> float:
        """Half its width, its parts included."""

    @property
    @abstractmethod
    def visits(self) -> int:
        """How many times it has entered its state (this time included)."""

    @abstractmethod
    def destroyed(self, part: str) -> bool:
        """Whether its part named `part` is destroyed."""

    @abstractmethod
    def shooter(self, target: Entity) -> Shooter:
        """What a gun needs to know about it, firing at `target`."""
