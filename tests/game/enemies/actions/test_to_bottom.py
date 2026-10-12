from pewpy.game.enemies.actions.to_bottom import ToBottom
from pewpy.game.enemies.screen import BOTTOM
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_jumps_just_below_the_screen() -> None:
    body = StandIn(x=0.2, y=0.5, height=0.1)
    assert ToBottom().do(body, Entity()) == []
    assert (body.x, body.y) == (0.2, BOTTOM - 0.1)
