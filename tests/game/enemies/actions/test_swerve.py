import pytest

from pewpy.game.enemies.actions.swerve import Swerve
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


@pytest.mark.parametrize(("player_x", "vx"), [(0.1, 0.2), (0.5, 0.4), (-0.5, -0.4)])
def test_swerving_heads_for_the_players_column_up_to_a_limit(player_x: float, vx: float) -> None:
    body = StandIn(x=0.0)
    assert Swerve(gain=2.0, limit=0.4).do(body, Entity(x=player_x)) == []
    assert body.vx == pytest.approx(vx)
