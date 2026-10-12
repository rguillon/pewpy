import pytest

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.motions.motion import Motion
from pewpy.game.entities import Entity
from tests.game.enemies.motions.moving import TARGET, enemy, move


class Rise(Motion):
    def apply(self, body: Body, dt: float, target: Entity, scroll_speed: float) -> None:  # noqa: ARG002 - as every motion
        body.vy = 1.0


def test_a_motion_must_say_how_it_moves() -> None:
    with pytest.raises(TypeError):
        Motion()  # ty: ignore[call-non-callable]


def test_a_motion_sets_the_speed_the_body_then_moves_with() -> None:
    riser = enemy(y=0.0)
    move(riser, Rise(), 0.5, TARGET)
    assert riser.y == pytest.approx(0.5)
