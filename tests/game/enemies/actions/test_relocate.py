import pytest

from pewpy.game.enemies.actions.relocate import Relocate
from pewpy.game.enemies.screen import HALF_WIDTH
from pewpy.game.entities import Entity
from tests.game.enemies.bodies import StandIn


def test_relocating_jumps_across_the_screen_and_down() -> None:
    body = StandIn(x=0.0, y=0.5, width=0.1)
    assert Relocate(step=0.25, dy=-0.2).do(body, Entity()) == []
    span = HALF_WIDTH - 0.1
    assert body.x == pytest.approx(span / 2)
    assert body.y == pytest.approx(0.3)


def test_relocating_past_the_side_wraps_round() -> None:
    span = HALF_WIDTH - 0.1
    body = StandIn(x=span / 2, width=0.1)
    Relocate(step=0.5).do(body, Entity())
    assert body.x == pytest.approx(-span / 2)
