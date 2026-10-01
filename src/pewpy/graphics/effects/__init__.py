"""Particle effects (placeholder until 05-visuals.md is decided): what every effect is; each one is in its own module
here. An effect throws out particles where something happened; particle_system.py moves them, effects_view.py draws
them. The helpers below are shared by the effects. Independent from Panda3D.

Positions are in world units: x right, y up the screen (like the game), z depth (away from the camera).
Particles are tiny cubes: "debris" is lit like the ships, "glow" (sparks, flashes) shines on its own.
"""

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

Color = tuple[float, float, float, float]

SPARK_COLORS: tuple[Color, ...] = ((1.0, 0.85, 0.4, 1), (1.0, 0.55, 0.15, 1), (1.0, 1.0, 0.8, 1))
BURN_COLORS: tuple[Color, ...] = ((0.6, 0.95, 1.0, 1), (1.0, 1.0, 1.0, 1), (0.3, 0.9, 1.0, 1))  # laser cyan


@dataclass(eq=False)
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    size: float  # edge of the cube at birth; it shrinks to nothing by the end of its life
    color: Color
    life: float  # seconds
    glow: bool = False
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0)  # tumbling axis (unit vector)
    spin: float = 0.0  # radians per second
    angle: float = 0.0
    age: float = 0.0
    grow: bool = False  # flashes swell quickly before shrinking

    @property
    def current_size(self) -> float:
        t = min(self.age / self.life, 1.0)
        if self.grow:
            return self.size * (min(t / 0.25, 1.0) if t < 0.25 else 1.0 - (t - 0.25) / 0.75)
        return self.size * (1.0 - t * t)


class Effect(ABC):
    """Something happening for an instant, seen as the particles it throws out."""

    @abstractmethod
    def particles(self, rng: random.Random) -> list[Particle]:
        """The particles it starts with (`rng` for their random spread)."""


def fireball(rng: random.Random, x: float, y: float, radius: float, colors: tuple[Color, ...]) -> list[Particle]:
    """A few glowing cubes that swell and shrink around (x, y): the brightest (`colors[0]`) in the middle."""
    result = []
    for i in range(6):
        distance = 0.0 if i == 0 else rng.uniform(0.3, 0.7) * radius
        heading = rng.uniform(0, 2 * math.pi)
        dx, dy = math.cos(heading) * distance, math.sin(heading) * distance
        result.append(
            Particle(
                x + dx, y + dy, 0.0, dx * 2, dy * 2, 0.0,
                size=radius * (0.9 if i == 0 else rng.uniform(0.35, 0.6)),
                color=colors[0] if i == 0 else rng.choice(colors[1:]),
                life=rng.uniform(0.16, 0.26),
                glow=True,
                grow=True,
                axis=unit((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))),
                spin=rng.uniform(-6, 6),
            )
        )  # fmt: skip
    return result


def burst(
    rng: random.Random,
    x: float,
    y: float,
    speed: tuple[float, float],
    size: tuple[float, float],
    life: tuple[float, float],
    colors: tuple[Color, ...],
    glow: bool = False,
) -> Particle:
    """One particle flying off in a random direction (mostly flat: the depth is a third of the rest)."""
    heading = rng.uniform(0, 2 * math.pi)
    velocity = rng.uniform(*speed)
    axis = unit((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
    return Particle(
        x, y, 0.0,
        math.cos(heading) * velocity, math.sin(heading) * velocity, rng.uniform(-0.33, 0.33) * velocity,
        size=rng.uniform(*size),
        color=rng.choice(colors),
        life=rng.uniform(*life),
        glow=glow,
        axis=axis,
        spin=rng.uniform(-12, 12),
    )  # fmt: skip


def unit(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(sum(value * value for value in vector)) or 1.0
    x, y, z = vector
    return x / length, y / length, z / length
