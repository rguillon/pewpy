import math

import pytest

from pewpy.game.enemies.body import Body
from pewpy.game.enemies.screen import HALF_WIDTH, TOP
from tests.game.enemies.bodies import StandIn


def test_a_body_must_say_its_health_span_visits_parts_and_guns() -> None:
    with pytest.raises(TypeError):
        Body()  # ty: ignore[call-non-callable]


@pytest.mark.parametrize(
    ("x", "y", "on_screen"),
    [
        (0.0, 0.0, True),
        (0.0, TOP + 0.01, False),
        (0.0, TOP, False),
        (HALF_WIDTH, 0.0, False),
        (-HALF_WIDTH + 0.01, 0.0, True),
    ],
)
def test_it_is_on_screen_below_the_top_and_between_the_sides(x: float, y: float, on_screen: bool) -> None:
    assert StandIn(x=x, y=y).on_screen is on_screen


def test_a_body_starts_heading_down_with_its_clocks_at_zero() -> None:
    body = StandIn()
    assert body.heading == -math.pi / 2
    assert (body.age, body.timer, body.clock, body.guns, body.base_x) == (0.0, 0.0, 0.0, [], None)
