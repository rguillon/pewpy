"""Running the particle effects (effects/): plays them, moves their particles and the lasers' light; effects_view.py
draws them. Independent from Panda3D.
"""

import math
import random
from collections.abc import Sequence

from pewpy.graphics.effects import Effect, Particle
from pewpy.graphics.effects.laser import LaserGlow, LaserLight

MAX_PARTICLES = 512  # the oldest go first when there are more
DRAG = 2.5  # how fast particles slow down, per second


class ParticleSystem:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
        self.particles: list[Particle] = []
        self.light = LaserLight()
        self.time = 0.0

    def play(self, effect: Effect) -> None:
        self.particles += effect.particles(self.rng)
        if len(self.particles) > MAX_PARTICLES:
            del self.particles[: len(self.particles) - MAX_PARTICLES]

    def set_lasers(self, lasers: Sequence[LaserGlow], dt: float) -> None:
        """The laser beams this frame (the player's, the enemies'), for their light."""
        self.light.set(lasers, dt, self.rng)

    def update(self, dt: float) -> None:
        self.time += dt
        self.light.update(dt, self.time)
        slow = math.exp(-DRAG * dt)
        for particle in self.particles:
            particle.age += dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.z += particle.vz * dt
            particle.vx *= slow
            particle.vy *= slow
            particle.vz *= slow
            particle.angle += particle.spin * dt
        self.particles = [particle for particle in self.particles if particle.age < particle.life]

    def clear(self) -> None:
        self.particles = []
        self.light.clear()
