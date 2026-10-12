import pytest

from pewpy import config
from pewpy.game.entities import Entity, Pickup


def test_an_entity_moves_with_its_speed() -> None:
    entity = Entity(x=0.1, y=0.2, vx=0.5, vy=-1.0)
    entity.move(0.1)
    assert (entity.x, entity.y) == (pytest.approx(0.15), pytest.approx(0.1))


@pytest.mark.parametrize(
    ("x", "y", "overlaps"),
    [
        (0.0, 0.0, True),
        (0.09, 0.0, True),
        (0.1, 0.0, False),
        (0.0, -0.09, True),
        (0.09, 0.09, True),
        (0.0, 0.11, False),
    ],
)
def test_hitboxes_overlap_when_they_cross(x: float, y: float, overlaps: bool) -> None:
    assert Entity(width=0.1, height=0.1).overlaps(Entity(x=x, y=y, width=0.1, height=0.1)) is overlaps


def test_the_play_area_reaches_a_margin_past_its_edges() -> None:
    top, side = config.PLAY_HEIGHT / 2, config.PLAY_WIDTH / 2
    assert Entity().in_play_area()
    assert Entity(x=side + 0.19).in_play_area()
    assert not Entity(x=-side - 0.2).in_play_area()
    assert not Entity(y=top + 0.2).in_play_area()
    assert not Entity(y=-top - 0.2).in_play_area()
    assert Entity(y=top + 0.5).in_play_area(top=top + 0.4)
    assert not Entity(x=0.5).in_play_area(margin=0.0, side=0.4)


def test_a_pickup_falls_slowly_and_is_a_repair_unless_told() -> None:
    pickup = Pickup()
    assert (pickup.kind, pickup.vy, pickup.width) == ("repair", -config.PICKUP_SPEED, config.PICKUP_SIZE)
