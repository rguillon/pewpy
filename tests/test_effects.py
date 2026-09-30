import math

import pytest

from pewpy import effects
from pewpy.effects import MAX_PARTICLES, Effects, Particle

RED = (1.0, 0.0, 0.0, 1.0)


def test_particles_fly_slow_down_and_disappear_at_the_end_of_their_life():
    fx = Effects(seed=0)
    fx.particles.append(Particle(0, 0, 0, 1.0, 0.0, 0.0, size=0.02, color=RED, life=0.5))
    fx.update(0.1)
    particle = fx.particles[0]
    assert particle.x == pytest.approx(0.1)  # moved at full speed first...
    assert particle.vx == pytest.approx(math.exp(-effects.DRAG * 0.1))  # ...then slowed down
    fx.update(0.5)
    assert fx.particles == []


def test_particles_shrink_while_flashes_swell_first():
    debris = Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0)
    flash = Particle(0, 0, 0, 0, 0, 0, size=0.02, color=RED, life=1.0, grow=True)
    sizes = []
    for age in (0.0, 0.2, 0.5, 0.99):
        debris.age = flash.age = age
        sizes.append((debris.current_size, flash.current_size))
    assert [debris for debris, _ in sizes] == sorted((debris for debris, _ in sizes), reverse=True)
    assert sizes[0][1] < sizes[1][1]  # the flash grows...
    assert sizes[3][1] < sizes[1][1]  # ...then shrinks


def test_impact_sparks_fly_back_where_the_shot_came_from():
    fx = Effects(seed=1)
    fx.impact(0.0, 0.0, towards=-1.0)
    assert 4 <= len(fx.particles) <= 6
    assert all(particle.vy < 0 and particle.glow for particle in fx.particles)


def test_explosions_throw_debris_in_the_colors_of_what_blew_up():
    fx = Effects(seed=2)
    fx.explosion(0.3, 0.4, size=0.1, colors=(RED,))
    debris = [particle for particle in fx.particles if not particle.glow]
    assert debris
    assert {particle.color for particle in debris} <= {RED, effects.DEBRIS_METAL}
    assert any(particle.grow for particle in fx.particles)  # the fireball
    small = len(fx.particles)
    fx.clear()
    fx.explosion(0.3, 0.4, size=0.2, colors=(RED,))
    assert len(fx.particles) > small  # bigger things make bigger explosions


def test_missile_blast_is_a_fireball_and_a_ring_of_sparks():
    fx = Effects(seed=3)
    fx.blast(0.0, 0.0, radius=0.1)
    assert all(particle.glow for particle in fx.particles)
    ring = [particle for particle in fx.particles if not particle.grow]
    assert len(ring) == 12


def test_laser_burn_makes_sparks_at_a_steady_rate():
    fx = Effects(seed=4)
    count = 0
    for _ in range(600):
        before = len(fx.particles)
        fx.burn(0.0, 0.5, 1 / 60)
        count += len(fx.particles) - before
    assert count == pytest.approx(effects.BURN_SPARKS * 10, rel=0.15)


def test_the_oldest_particles_go_first_when_there_are_too_many():
    fx = Effects(seed=5)
    for _ in range(100):
        fx.explosion(0.0, 0.0, size=0.2, colors=(RED,))
    assert len(fx.particles) == MAX_PARTICLES
