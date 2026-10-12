import pytest

from pewpy.game.enemies.motions.scroll import Scroll
from tests.game.enemies.motions.moving import SCROLL, enemy, move


def test_scrolling_with_the_ground_maybe_driving_too() -> None:
    truck = enemy(vx=0.1)
    move(truck, Scroll(plus=-0.15))
    assert (truck.vx, truck.vy) == (0.1, pytest.approx(-0.35))
    mine = enemy(vx=0.1)
    move(mine, Scroll(stop_x=True))
    assert (mine.vx, mine.vy) == (0.0, -SCROLL)
