import pytest

from pewpy.game.weapons.enemy.shots import WaveBullet

DT = 1 / 60


def test_wave_bullets_snake_across_their_line_of_flight():
    bullet = WaveBullet(x=0.0, y=0.5, vx=0.0, vy=-0.45, hostile=True)
    sideways = []
    for _ in range(round(0.7 / DT)):
        bullet.move(DT)
        sideways.append(bullet.x)
    assert min(sideways) < -0.05 < 0.05 < max(sideways)
    assert bullet.y == pytest.approx(0.5 - 0.45 * 0.7, abs=1e-6)
