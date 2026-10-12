from pewpy.game.enemies.actions.velocity import Velocity
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_sets_the_speeds_given_and_keeps_the_others() -> None:
    body = StandIn(vx=0.1, vy=0.2)
    assert Velocity(vy=-0.5).do(body, Entity()) == []
    assert (body.vx, body.vy) == (0.1, -0.5)
    Velocity(vx=0.3).do(body, Entity())
    assert (body.vx, body.vy) == (0.3, -0.5)
    Velocity(vx=0.0, vy=0.0).do(body, Entity())
    assert (body.vx, body.vy) == (0.0, 0.0)
