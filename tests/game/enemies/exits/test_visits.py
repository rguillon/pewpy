from pewpy.game.enemies.exits.visits import Visits
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_once_the_state_has_been_entered_that_many_times() -> None:
    assert not Visits(3).holds(StandIn(entered=2), Entity())
    assert Visits(3).holds(StandIn(entered=3), Entity())
