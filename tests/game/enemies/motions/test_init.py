import pytest

from pewpy.game.enemies.errors import UnknownNameError
from pewpy.game.enemies.motions import MOTIONS, Steer, parse_motion


def test_a_motion_is_read_from_its_type_and_fields() -> None:
    assert parse_motion({"type": "steer", "rate": 1.0, "goal": "down"}) == Steer(rate=1.0, goal="down")


def test_every_motion_is_named_by_its_type() -> None:
    assert all(parse_motion({"type": name}) == motion() for name, motion in MOTIONS.items())


def test_an_unknown_motion_is_refused() -> None:
    with pytest.raises(UnknownNameError, match="unknown motion 'teleport'"):
        parse_motion({"type": "teleport"})
