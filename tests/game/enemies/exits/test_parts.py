from pewpy.game.enemies.exits.parts import Parts
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_it_holds_once_every_part_named_is_destroyed() -> None:
    both = Parts(("left", "right"))
    assert not both.holds(StandIn(lost=("left",)), Entity())
    assert both.holds(StandIn(lost=("left", "right", "core")), Entity())
