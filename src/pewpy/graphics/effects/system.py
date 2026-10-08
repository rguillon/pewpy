"""Running the particle effects (this package): plays them, moves their particles and the lasers' light.

view.py draws them. Independent from Panda3D.
"""

import math
import random
from collections.abc import Sequence

from pewpy.graphics.effects import Effect, Particle
from pewpy.graphics.effects.laser import LaserGlow, LaserLight

MAX_PARTICLES = 512  # the oldest go first when there are more
DRAG = 2.5  # how fast particles slow down, per second


class ParticleSystem:
    """The particles in play and the lasers' light."""

    def __init__(self, seed: int | None = None) -> None:
        """Start with no particles, at time zero, with `seed` making the randomness (None: the clock)."""
        self.rng = random.Random(seed)
        self.particles: list[Particle] = []
        self.light = LaserLight()
        self.time = 0.0

    def play(self, effect: Effect) -> None:
        """Play an effect: add its particles (the oldest go beyond MAX_PARTICLES)."""
        self.particles += effect.particles(self.rng)
        if len(self.particles) > MAX_PARTICLES:
            del self.particles[: len(self.particles) - MAX_PARTICLES]

    def set_lasers(self, lasers: Sequence[LaserGlow], dt: float) -> None:
        """Set the laser beams this frame (the player's, the enemies'), for their light."""
        self.light.set(lasers, dt, self.rng)

    def update(self, dt: float) -> None:
        """Move the particles and the light on by `dt` seconds; the dead particles go."""
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
        """Remove every particle and the light."""
        self.particles = []
        self.light.clear()
