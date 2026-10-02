import math

import pytest

from pewpy.graphics.effects import Particle, system
from pewpy.graphics.effects.explosion import Explosion
from pewpy.graphics.effects.laser import LaserGlow
from pewpy.graphics.effects.system import MAX_PARTICLES, ParticleSystem

RED = (1.0, 0.0, 0.0, 1.0)
DT = 1 / 60


def test_particles_fly_slow_down_and_disappear_at_the_end_of_their_life() -> None:
    fx = ParticleSystem(seed=0)
    fx.particles.append(Particle(0, 0, 0, 1.0, 0.0, 0.0, size=0.02, color=RED, life=0.5))
    fx.update(0.1)
    particle = fx.particles[0]
    assert particle.x == pytest.approx(0.1)  # moved at full speed first...
    assert particle.vx == pytest.approx(math.exp(-system.DRAG * 0.1))  # ...then slowed down
    fx.update(0.5)
    assert fx.particles == []


def test_a_played_effect_adds_its_particles() -> None:
    fx = ParticleSystem(seed=2)
    fx.play(Explosion(0.3, 0.4, size=0.1, colors=(RED,)))
    assert fx.particles


def test_the_oldest_particles_go_first_when_there_are_too_many() -> None:
    fx = ParticleSystem(seed=5)
    for _ in range(100):
        fx.play(Explosion(0.0, 0.0, size=0.2, colors=(RED,)))
    assert len(fx.particles) == MAX_PARTICLES


def test_the_laser_light_follows_the_laser_and_clear_puts_everything_out() -> None:
    fx = ParticleSystem(seed=0)
    beam = LaserGlow(x=0.2, bottom=-0.5, top=0.5, width=0.03)
    for _ in range(10):
        fx.set_lasers([beam], DT)
        fx.update(DT)
    assert fx.light.lasers == {0: beam}
    assert fx.light.photons
    fx.play(Explosion(0.0, 0.0, size=0.1, colors=(RED,)))
    fx.clear()
    assert fx.particles == []
    assert fx.light.photons == []
    assert fx.light.lasers == {}
