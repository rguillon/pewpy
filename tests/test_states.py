import pytest

from pewpy.states import InvalidTransitionError, State, StateMachine


def test_starts_in_main_menu():
    assert StateMachine().state is State.MAIN_MENU


def test_full_game_flow():
    changes = []
    machine = StateMachine(on_change=lambda previous, current: changes.append((previous, current)))
    for state in [
        State.WORLD_SELECT,
        State.LEVEL_SELECT,
        State.PLAYING,
        State.PAUSED,
        State.PLAYING,
        State.GAME_OVER,
        State.PLAYING,
        State.GAME_OVER,
        State.PLAYING,
        State.LEVEL_COMPLETE,
        State.PLAYING,
        State.LEVEL_COMPLETE,
        State.MAIN_MENU,
    ]:
        machine.transition(state)
    assert machine.state is State.MAIN_MENU
    assert changes[:2] == [(State.MAIN_MENU, State.WORLD_SELECT), (State.WORLD_SELECT, State.LEVEL_SELECT)]
    assert len(changes) == 13


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (State.MAIN_MENU, State.PLAYING),
        (State.MAIN_MENU, State.LEVEL_SELECT),  # through the world select
        (State.WORLD_SELECT, State.PLAYING),
        (State.PLAYING, State.MAIN_MENU),
        (State.PAUSED, State.GAME_OVER),
        (State.LEVEL_SELECT, State.PAUSED),
        (State.LEVEL_COMPLETE, State.PAUSED),
    ],
)
def test_invalid_transition_is_refused(start, target):
    machine = StateMachine(initial=start)
    with pytest.raises(InvalidTransitionError):
        machine.transition(target)
    assert machine.state is start


def test_the_models_screen_opens_from_the_main_menu_and_goes_back_to_it():
    machine = StateMachine()
    machine.transition(State.MODELS)
    assert not machine.can_transition(State.PLAYING)
    machine.transition(State.MAIN_MENU)
    assert machine.state is State.MAIN_MENU
