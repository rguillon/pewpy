import random

from pewpy.graphics.effects.impact import Impact

RED = (1.0, 0.0, 0.0, 1.0)


def test_impact_sparks_fly_back_where_the_shot_came_from():
    sparks = Impact(0.0, 0.0, towards=-1.0).particles(random.Random(1))  # noqa: S311
    assert 4 <= len(sparks) <= 6
    assert all(particle.vy < 0 and particle.glow for particle in sparks)


def test_impact_sparks_can_take_a_color():
    sparks = Impact(0.0, 0.0, towards=1.0, color=RED).particles(random.Random(1))  # noqa: S311
    assert all(particle.vy > 0 and particle.color == RED for particle in sparks)
