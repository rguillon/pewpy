import pytest

from pewpy.game.enemies.actions import ACTIONS, Fire, Sway, parse_action
from pewpy.game.enemies.errors import UnknownNameError
from pewpy.game.weapons.guns import parse_gun


def test_an_action_is_read_from_its_type_and_fields() -> None:
    assert parse_action({"type": "sway", "speed": 0.2}) == Sway(speed=0.2)


def test_an_actions_gun_is_read_as_a_gun() -> None:
    gun = {"pattern": "ring", "count": 8, "interval": 1.0, "speed": 0.4}
    assert parse_action({"type": "fire", "gun": gun}) == Fire(parse_gun(gun))


def test_every_action_is_named_by_its_type() -> None:
    assert all(type(parse_action({"type": name})) is action for name, action in ACTIONS.items() if name != "fire")


def test_an_unknown_action_is_refused() -> None:
    with pytest.raises(UnknownNameError, match="unknown action 'explode'"):
        parse_action({"type": "explode"})
