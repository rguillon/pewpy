from pewpy.game.enemies.errors import EnemySpecError, FlagError, UnknownConditionError, UnknownNameError


def test_a_wrong_description_says_which_one() -> None:
    assert str(EnemySpecError("drone.json", "no size")) == "drone.json: no size"


def test_an_unknown_name_says_what_it_was_given_as() -> None:
    error = UnknownNameError("motion", "teleport")
    assert isinstance(error, ValueError)
    assert str(error) == "unknown motion 'teleport'"


def test_an_unknown_condition_is_an_unknown_name() -> None:
    error = UnknownConditionError("soon")
    assert isinstance(error, UnknownNameError)
    assert str(error) == "unknown exit condition 'soon'"


def test_a_flag_can_only_be_true() -> None:
    assert str(FlagError("idle")) == "idle can only be true"
