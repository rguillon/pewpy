from pewpy.game.enemies.exits.above_y import AboveY
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_at_or_above_its_height() -> None:
    above = AboveY(0.5)
    assert above.holds(StandIn(y=0.6), Entity())
    assert above.holds(StandIn(y=0.5), Entity())
    assert not above.holds(StandIn(y=0.4), Entity())
