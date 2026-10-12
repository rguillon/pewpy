from pewpy.game.enemies.exits.timer import Timer
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_once_the_states_timer_runs_out() -> None:
    assert not Timer().holds(StandIn(timer=0.1), Entity())
    assert Timer().holds(StandIn(timer=0.0), Entity())
    assert Timer().holds(StandIn(timer=-0.1), Entity())
