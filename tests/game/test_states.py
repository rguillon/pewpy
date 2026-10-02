import pytest

from pewpy.game.states import InvalidTransitionError, State, StateMachine


def test_starts_in_main_menu() -> None:
    assert StateMachine().state is State.MAIN_MENU


def test_full_game_flow() -> None:
    changes = []
    machine = StateMachine(on_change=lambda previous, current: changes.append((previous, current)))
    for state in [
        State.SHIP_SELECT,
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
    assert changes[:3] == [
        (State.MAIN_MENU, State.SHIP_SELECT),
        (State.SHIP_SELECT, State.WORLD_SELECT),
        (State.WORLD_SELECT, State.LEVEL_SELECT),
    ]
    assert len(changes) == 14


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (State.MAIN_MENU, State.PLAYING),
        (State.MAIN_MENU, State.LEVEL_SELECT),  # through the world select
        (State.MAIN_MENU, State.WORLD_SELECT),  # through the ship select
        (State.SHIP_SELECT, State.PLAYING),
        (State.WORLD_SELECT, State.PLAYING),
        (State.PLAYING, State.MAIN_MENU),
        (State.PAUSED, State.GAME_OVER),
        (State.LEVEL_SELECT, State.PAUSED),
        (State.LEVEL_COMPLETE, State.PAUSED),
    ],
)
def test_invalid_transition_is_refused(start: State, target: State) -> None:
    machine = StateMachine(initial=start)
    with pytest.raises(InvalidTransitionError):
        machine.transition(target)
    assert machine.state is start


def test_the_ship_select_goes_back_to_the_main_menu_and_the_world_select_back_to_it() -> None:
    machine = StateMachine()
    machine.transition(State.SHIP_SELECT)
    machine.transition(State.MAIN_MENU)
    machine.transition(State.SHIP_SELECT)
    machine.transition(State.WORLD_SELECT)
    assert not machine.can_transition(State.MAIN_MENU)
    machine.transition(State.SHIP_SELECT)
    assert machine.state is State.SHIP_SELECT
