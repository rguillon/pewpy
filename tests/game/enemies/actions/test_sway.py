import pytest

from pewpy import config
from pewpy.game.enemies.actions.sway import Sway
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


@pytest.mark.parametrize(("vx", "way"), [(0.0, 1), (0.3, 1), (-0.3, -1)])
def test_swaying_keeps_the_way_it_was_going_right_if_still(vx: float, way: int) -> None:
    body = StandIn(vx=vx)
    assert Sway(speed=0.1).do(body, Entity()) == []
    assert body.vx == pytest.approx(way * 0.1 * config.WIDTH_SCALE)
