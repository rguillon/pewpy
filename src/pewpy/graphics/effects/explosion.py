"""Something blowing up: a fireball, sparks and debris."""

import math
import random
from dataclasses import dataclass

from pewpy.graphics.effects import SPARK_COLORS, Color, Effect, Particle, burst, fireball

FIRE_COLORS: tuple[Color, ...] = ((1.0, 0.95, 0.7, 1), (1.0, 0.75, 0.3, 1), (1.0, 0.5, 0.15, 1), (0.9, 0.3, 0.1, 1))
DEBRIS_METAL: Color = (0.3, 0.31, 0.35, 1)


@dataclass(frozen=True)
class Explosion(Effect):
    """Something `size` wide blows up: a fireball, sparks, and debris in its `colors` (plus some metal)."""

    x: float
    y: float
    size: float
    colors: tuple[Color, ...]

    def particles(self, rng: random.Random) -> list[Particle]:
        """Throw out a fireball, debris and sparks, more for a bigger enemy."""
        x, y, size = self.x, self.y, self.size
        scale = size / 0.1  # sizes and speeds are tuned for a 0.1-wide enemy
        result = fireball(rng, x, y, size * 0.7, FIRE_COLORS)
        for _ in range(round(8 * math.sqrt(scale))):
            result.append(
                burst(
                    rng, x, y, speed=(0.6, 1.4), size=(0.006, 0.012), life=(0.2, 0.45), colors=SPARK_COLORS, glow=True
                )
            )
        debris_colors = (*self.colors, DEBRIS_METAL)
        for _ in range(round(14 * scale) + 4):
            result.append(
                burst(
                    rng, x, y, speed=(0.25, 0.85), size=(0.1 * size, 0.22 * size), life=(0.5, 1.0), colors=debris_colors
                )
            )
        return result
