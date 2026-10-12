from pewpy.game.enemies.exits.volleys import Volleys
from pewpy.game.entities import Entity
from pewpy.game.weapons.guns import GunState
from tests.game.enemies.bodies import StandIn


def test_it_holds_once_the_guns_fired_that_many_volleys_between_them() -> None:
    guns = [GunState(0.0, volleys=1), GunState(0.0, volleys=2)]
    assert Volleys(3).holds(StandIn(guns=guns), Entity())
    assert not Volleys(4).holds(StandIn(guns=guns), Entity())


def test_it_is_checked_after_the_guns_fire() -> None:
    assert Volleys(1).after_guns
