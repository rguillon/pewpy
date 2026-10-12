import pytest

from pewpy.game.enemies.actions.toward_middle import TowardMiddle
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


@pytest.mark.parametrize(("x", "vx"), [(-0.4, 0.2), (0.0, 0.2), (0.4, -0.2)])
def test_it_heads_sideways_for_the_middle(x: float, vx: float) -> None:
    body = StandIn(x=x)
    assert TowardMiddle(speed=0.2).do(body, Entity()) == []
    assert body.vx == vx
