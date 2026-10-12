import pytest

from pewpy import config
from pewpy.game.weapons.bullets.beam import BEAM_BOTTOM, beam

DT = 1 / 60


def test_a_beam_goes_down_past_the_bottom_of_the_screen_for_a_while() -> None:
    shot = beam(0.2, 0.5, 0.04, 0.5)
    assert (shot.x, shot.width, shot.pierces, shot.style) == (0.2, 0.04, True, "beam")
    assert (shot.hostile, shot.damage) == (True, config.ENEMY_BULLET_DAMAGE)
    assert shot.y + shot.height / 2 == pytest.approx(0.5)
    assert shot.y - shot.height / 2 == pytest.approx(BEAM_BOTTOM)
    assert BEAM_BOTTOM < -config.PLAY_HEIGHT / 2
    for _ in range(round(0.4 / DT)):
        shot.move(DT)
    assert shot.alive
    for _ in range(round(0.2 / DT)):
        shot.move(DT)
    assert not shot.alive


def test_a_beam_stays_at_its_muzzles_depth() -> None:
    shot = beam(0.2, 0.5, 0.04, 0.5, depth=-0.05)
    shot.move(0.1)
    assert shot.depth == -0.05
