"""A shot hitting something: a few quick sparks."""

import math
import random
from dataclasses import dataclass

from pewpy.graphics.effects import SPARK_COLORS, Color, Effect, Particle


@dataclass(frozen=True)
class Impact(Effect):
    """A few quick sparks where a shot hits, thrown mostly `towards` (+1 up the screen, -1 down)."""

    x: float
    y: float
    towards: float = -1.0
    color: Color | None = None  # None: spark colors

    def particles(self, rng: random.Random) -> list[Particle]:
        result = []
        for _ in range(rng.randint(4, 6)):
            angle = math.radians(90 * self.towards + rng.uniform(-60, 60))
            speed = rng.uniform(0.4, 1.0)
            result.append(
                Particle(
                    self.x, self.y, 0.0,
                    math.cos(angle) * speed, math.sin(angle) * speed, rng.uniform(-0.2, 0.2),
                    size=rng.uniform(0.006, 0.011),
                    color=self.color or rng.choice(SPARK_COLORS),
                    life=rng.uniform(0.12, 0.25),
                    glow=True,
                )
            )  # fmt: skip
        return result
