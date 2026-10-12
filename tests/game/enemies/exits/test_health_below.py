from pewpy.game.enemies.exits.health_below import HealthBelow
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_below_its_share_of_the_full_health() -> None:
    half = HealthBelow(0.5)
    assert not half.holds(StandIn(health=5.0, full=10.0), Entity())
    assert half.holds(StandIn(health=4.9, full=10.0), Entity())
