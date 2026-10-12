from pewpy.game.enemies.exits.below_y import BelowY
from pewpy.game.enemies.exits.clock import Clock
from pewpy.game.enemies.exits.exit import Exit
from pewpy.game.enemies.exits.volleys import Volleys
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_an_exit_opens_once_all_its_conditions_hold() -> None:
    way_out = Exit("next", (BelowY(0.5), Clock(1.0)))
    assert not way_out.open(StandIn(y=0.4, clock=0.5), Entity())
    assert not way_out.open(StandIn(y=0.6, clock=1.5), Entity())
    assert way_out.open(StandIn(y=0.4, clock=1.5), Entity())


def test_an_exit_without_conditions_is_always_open() -> None:
    assert Exit("next").open(StandIn(), Entity())


def test_an_exit_is_checked_after_the_guns_if_any_of_its_conditions_is() -> None:
    assert not Exit("next", (Clock(1.0),)).after_guns
    assert Exit("next", (Clock(1.0), Volleys(2))).after_guns
