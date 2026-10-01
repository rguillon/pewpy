import random

from pewpy.graphics.effects import Particle, burst, fireball, unit

RED = (1.0, 0.0, 0.0, 1.0)


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


def test_a_fireball_is_brightest_in_the_middle_and_swells():
    white = (1.0, 1.0, 1.0, 1.0)
    flames = fireball(random.Random(0), 0.2, 0.3, 0.1, (white, RED))  # noqa: S311
    assert (flames[0].x, flames[0].y, flames[0].color) == (0.2, 0.3, white)
    assert all(flame.glow and flame.grow for flame in flames)
    assert all(flame.color == RED for flame in flames[1:])


def test_a_burst_flies_off_mostly_flat_within_its_ranges():
    for seed in range(20):
        rng = random.Random(seed)  # noqa: S311
        particle = burst(rng, 0.0, 0.0, speed=(0.5, 1.0), size=(0.01, 0.02), life=(0.2, 0.4), colors=(RED,))
        flat = (particle.vx**2 + particle.vy**2) ** 0.5
        assert 0.5 <= flat <= 1.0
        assert abs(particle.vz) <= flat / 3 + 1e-9
        assert 0.01 <= particle.size <= 0.02 and 0.2 <= particle.life <= 0.4


def test_unit_vectors_have_a_length_of_one_and_zero_stays_zero():
    x, y, z = unit((3.0, 0.0, 4.0))
    assert (x, y, z) == (0.6, 0.0, 0.8)
    assert unit((0.0, 0.0, 0.0)) == (0.0, 0.0, 0.0)
