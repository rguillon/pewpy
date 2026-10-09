import pytest

from pewpy.game.weapons.bullets import BEAM_BOTTOM, Bullet, WaveBullet, beam
from pewpy.game.weapons.bullets.bullet import SETTLE_SPEED

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


def test_a_shot_fired_off_the_play_plane_goes_back_to_it() -> None:
    shot = Bullet(vy=-0.5, depth=-0.1)
    shot.move(0.1)
    assert shot.depth == pytest.approx(-0.1 + SETTLE_SPEED * 0.1)
    for _ in range(60):
        shot.move(DT)
    assert shot.depth == 0.0
    under = Bullet(depth=0.01)
    under.move(0.1)
    assert under.depth == 0.0


def test_a_beam_stays_at_its_muzzles_depth() -> None:
    shot = beam(0.2, 0.5, 0.04, 0.5, depth=-0.05)
    shot.move(0.1)
    assert shot.depth == -0.05
