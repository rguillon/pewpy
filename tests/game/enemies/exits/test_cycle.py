import pytest

from pewpy.game.enemies.exits.cycle import Cycle
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


@pytest.mark.parametrize(("age", "holds"), [(0.4, False), (0.5, True), (0.9, True), (1.0, False), (2.6, True)])
def test_it_holds_in_its_part_of_each_period(age: float, holds: bool) -> None:
    assert Cycle(2.0, 0.5, 1.0).holds(StandIn(age=age), Entity()) is holds
