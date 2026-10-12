import pytest

from pewpy.game.enemies.actions.aim import Aim
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_aiming_flies_straight_at_the_player() -> None:
    body = StandIn(x=0.0, y=0.5)
    assert Aim(speed=0.5).do(body, Entity(x=0.3, y=0.1)) == []
    assert (body.vx, body.vy) == (pytest.approx(0.3), pytest.approx(-0.4))


def test_already_on_the_player_it_stops() -> None:
    body = StandIn(x=0.2, y=0.2, vx=1.0)
    Aim(speed=0.5).do(body, Entity(x=0.2, y=0.2))
    assert (body.vx, body.vy) == (0.0, 0.0)
