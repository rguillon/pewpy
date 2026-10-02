"""The laser burning something: a steady trickle of sparks."""

import math
import random
from dataclasses import dataclass

from pewpy.graphics.effects import BURN_COLORS, Effect, Particle

BURN_SPARKS = 40.0  # per second while the laser touches an enemy


@dataclass(frozen=True)
class Burn(Effect):
    """One frame (`dt` seconds) of the laser burning what it touches at (x, y).

    BURN_SPARKS sparks per second on average, thrown back down and to the sides.
    """

    x: float
    y: float
    dt: float

    def particles(self, rng: random.Random) -> list[Particle]:
        """Throw out this frame's sparks."""
        result = []
        count = BURN_SPARKS * self.dt
        for _ in range(int(count) + (rng.random() < count % 1)):
            angle = math.radians(rng.uniform(-150, -30))
            speed = rng.uniform(0.3, 0.8)
            result.append(
                Particle(
                    self.x + rng.uniform(-0.01, 0.01), self.y, 0.0,
                    math.cos(angle) * speed, math.sin(angle) * speed, rng.uniform(-0.2, 0.2),
                    size=rng.uniform(0.005, 0.009),
                    color=rng.choice(BURN_COLORS),
                    life=rng.uniform(0.1, 0.2),
                    glow=True,
                )
            )  # fmt: skip
        return result
