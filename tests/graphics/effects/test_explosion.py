import random

from pewpy.graphics.effects.explosion import DEBRIS_METAL, Explosion

RED = (1.0, 0.0, 0.0, 1.0)


def test_explosions_throw_debris_in_the_colors_of_what_blew_up():
    particles = Explosion(0.3, 0.4, size=0.1, colors=(RED,)).particles(random.Random(2))  # noqa: S311
    debris = [particle for particle in particles if not particle.glow]
    assert debris
    assert {particle.color for particle in debris} <= {RED, DEBRIS_METAL}
    assert any(particle.grow for particle in particles)  # the fireball


def test_bigger_things_make_bigger_explosions():
    small = Explosion(0.3, 0.4, size=0.1, colors=(RED,)).particles(random.Random(2))  # noqa: S311
    big = Explosion(0.3, 0.4, size=0.2, colors=(RED,)).particles(random.Random(2))  # noqa: S311
    assert len(big) > len(small)
