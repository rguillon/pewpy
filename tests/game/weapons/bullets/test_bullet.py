import pytest

from pewpy.game.weapons.bullets.bullet import SETTLE_SPEED, Bullet

DT = 1 / 60


def test_a_bullet_flies_with_its_speed_until_it_leaves_the_screen() -> None:
    shot = Bullet(x=0.1, y=0.0, vy=0.5)
    for _ in range(600):
        shot.move(DT)
    assert shot.alive  # no life of its own: the world takes it away off screen
    assert shot.y == pytest.approx(5.0)


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


def test_a_shot_with_a_life_vanishes_when_it_runs_out() -> None:
    shot = Bullet(life=0.1)
    shot.move(0.05)
    assert shot.alive
    shot.move(0.05)
    assert not shot.alive
