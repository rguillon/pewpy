import pytest

from pewpy.game.enemies.actions.velocity import Velocity
from pewpy.game.enemies.errors import FlagError, UnknownConditionError
from pewpy.game.enemies.exits import CONDITIONS, Exit, flag, parse_exit
from pewpy.game.enemies.exits.below_y import BelowY
from pewpy.game.enemies.exits.cycle import Cycle
from pewpy.game.enemies.exits.idle import Idle
from pewpy.game.enemies.exits.parts import Parts
from pewpy.game.enemies.exits.timer import Timer


def test_an_exit_is_read_with_its_actions_and_conditions() -> None:
    read = parse_exit({
        "to": "dive",
        "then": [{"type": "velocity", "vy": -0.5}],
        "go_on": True,
        "below_y": 0.3,
        "cycle": [2.0, 0.0, 1.0],
        "parts": ["left", "right"],
        "idle": True,
    })
    conditions = (BelowY(0.3), Cycle(2.0, 0.0, 1.0), Parts(("left", "right")), Idle())
    assert read == Exit("dive", conditions, (Velocity(vy=-0.5),), go_on=True, recheck=False)


def test_an_exit_with_nothing_but_its_state_is_always_taken() -> None:
    assert parse_exit({"to": "a"}) == Exit("a")


def test_an_unknown_condition_is_refused() -> None:
    with pytest.raises(UnknownConditionError, match="unknown exit condition 'soon'"):
        parse_exit({"to": "a", "soon": True})


def test_a_flag_is_only_ever_true() -> None:
    assert flag("timer", Timer())(True)  # noqa: FBT003 - the value read == Timer()
    with pytest.raises(FlagError, match="timer can only be true"):
        CONDITIONS["timer"](False)  # noqa: FBT003 - the value read
