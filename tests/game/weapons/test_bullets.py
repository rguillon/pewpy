import pytest

from pewpy.game.weapons.bullets import BEAM_BOTTOM, WaveBullet, beam

DT = 1 / 60


def test_wave_bullets_snake_across_their_line_of_flight() -> None:
    bullet = WaveBullet(x=0.0, y=0.5, vx=0.0, vy=-0.45, hostile=True)
    sideways = []
    for _ in range(round(0.7 / DT)):
        bullet.move(DT)
        sideways.append(bullet.x)
    assert min(sideways) < -0.05 < 0.05 < max(sideways)
    assert bullet.y == pytest.approx(0.5 - 0.45 * 0.7, abs=1e-6)


def test_a_beam_goes_down_past_the_bottom_of_the_screen_for_a_while() -> None:
    shot = beam(0.2, 0.5, 0.04, 0.5)
    assert (shot.x, shot.width, shot.pierces, shot.style) == (0.2, 0.04, True, "beam")
    assert shot.y + shot.height / 2 == pytest.approx(0.5)
    assert shot.y - shot.height / 2 == pytest.approx(BEAM_BOTTOM)
    for _ in range(round(0.4 / DT)):
        shot.move(DT)
    assert shot.alive
    for _ in range(round(0.2 / DT)):
        shot.move(DT)
    assert not shot.alive
