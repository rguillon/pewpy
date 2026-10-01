import random

from pewpy.graphics.effects.blast import Blast


def test_missile_blast_is_a_fireball_and_a_ring_of_sparks():
    particles = Blast(0.0, 0.0, radius=0.1).particles(random.Random(3))  # noqa: S311
    assert all(particle.glow for particle in particles)
    ring = [particle for particle in particles if not particle.grow]
    assert len(ring) == 12
