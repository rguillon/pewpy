import pytest

from pewpy.game.weapons.bullets.wave import WaveBullet

DT = 1 / 60


def test_wave_bullets_snake_across_their_line_of_flight() -> None:
    bullet = WaveBullet(x=0.0, y=0.5, vx=0.0, vy=-0.45, hostile=True)
    sideways = []
    for _ in range(round(0.7 / DT)):
        bullet.move(DT)
        sideways.append(bullet.x)
    assert min(sideways) < -0.05 < 0.05 < max(sideways)
    assert bullet.y == pytest.approx(0.5 - 0.45 * 0.7, abs=1e-6)


def test_a_wave_bullet_flying_sideways_snakes_up_and_down() -> None:
    bullet = WaveBullet(x=0.0, y=0.0, vx=0.5, amplitude=0.1, period=1.0)
    bullet.move(0.25)
    assert bullet.x == pytest.approx(0.125)
    assert bullet.y == pytest.approx(0.1)
