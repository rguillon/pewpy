from pewpy.game.enemies.exits.aligned import Aligned
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_within_reach_of_the_players_column_either_side() -> None:
    aligned = Aligned(0.1)
    assert aligned.holds(StandIn(x=0.3, y=0.9), Entity(x=0.25, y=-0.8))
    assert aligned.holds(StandIn(x=0.2), Entity(x=0.3))
    assert not aligned.holds(StandIn(x=0.0), Entity(x=0.3))
    assert not aligned.holds(StandIn(x=0.3), Entity(x=-0.3))
