import pytest

from pewpy.game.enemies.actions.action import Action
from pewpy.game.enemies.body import Body
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


class Stop(Action):
    def do(self, body: Body, target: Entity) -> list[Entity]:  # noqa: ARG002 - as every action
        body.vx = body.vy = 0.0
        return []


def test_an_action_must_say_what_it_does() -> None:
    with pytest.raises(TypeError):
        Action()  # ty: ignore[call-non-callable]


def test_an_action_changes_the_body_and_returns_what_it_made() -> None:
    body = StandIn(vx=1.0, vy=1.0)
    assert Stop().do(body, Entity()) == []
    assert (body.vx, body.vy) == (0.0, 0.0)
