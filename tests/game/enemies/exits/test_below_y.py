from pewpy.game.enemies.exits.below_y import BelowY
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_at_or_below_its_height() -> None:
    below = BelowY(0.5)
    assert below.holds(StandIn(y=0.4), Entity())
    assert below.holds(StandIn(y=0.5), Entity())
    assert not below.holds(StandIn(y=0.6), Entity())
