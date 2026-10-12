import pytest

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.exits.condition import Condition
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


class Always(Condition):
    def holds(self, body: Body, target: Entity) -> bool:  # noqa: ARG002 - as every condition
        return True


def test_a_condition_must_say_when_it_holds() -> None:
    with pytest.raises(TypeError):
        Condition()  # ty: ignore[call-non-callable]


def test_a_condition_is_checked_before_the_enemy_moves_unless_told() -> None:
    assert not Always().after_guns
    assert Always().holds(StandIn(), Entity())
