from pewpy.game.enemies.exits.clock import Clock
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_once_that_long_in_the_state() -> None:
    clock = Clock(2.0)
    assert not clock.holds(StandIn(clock=1.9), Entity())
    assert clock.holds(StandIn(clock=2.0), Entity())
