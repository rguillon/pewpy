"""A missile's explosion: a fireball and a ring of sparks."""

import math
import random
from dataclasses import dataclass

from pewpy.graphics.effects import Color, Effect, Particle, fireball

BLAST_COLORS: tuple[Color, ...] = ((1.0, 0.85, 0.4, 1), (1.0, 0.6, 0.15, 1), (1.0, 0.35, 0.1, 1))


@dataclass(frozen=True)
class Blast(Effect):
    """A missile's explosion: an orange fireball about as wide as its splash (`radius`) and a ring of sparks."""

    x: float
    y: float
    radius: float

    def particles(self, rng: random.Random) -> list[Particle]:
        """Throw out a fireball and a ring of sparks."""
        result = fireball(rng, self.x, self.y, self.radius, BLAST_COLORS)
        for i in range(12):
            angle = 2 * math.pi * i / 12 + rng.uniform(-0.2, 0.2)
            speed = rng.uniform(0.6, 1.0)
            result.append(
                Particle(
                    self.x, self.y, 0.0, math.cos(angle) * speed, math.sin(angle) * speed, 0.0,
                    size=rng.uniform(0.008, 0.014),
                    color=rng.choice(BLAST_COLORS),
                    life=rng.uniform(0.2, 0.35),
                    glow=True,
                )
            )  # fmt: skip
        return result
