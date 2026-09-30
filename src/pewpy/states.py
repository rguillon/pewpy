"""Global game state machine (01-gameplay.md, "Global state")."""

from collections.abc import Callable
from enum import Enum, auto


class State(Enum):
    MAIN_MENU = auto()
    MODELS = auto()  # every model on show, for working on them
    WORLD_SELECT = auto()
    LEVEL_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()


TRANSITIONS: dict[State, frozenset[State]] = {
    State.MAIN_MENU: frozenset({State.WORLD_SELECT, State.MODELS}),
    State.MODELS: frozenset({State.MAIN_MENU}),
    State.WORLD_SELECT: frozenset({State.LEVEL_SELECT, State.MAIN_MENU}),
    State.LEVEL_SELECT: frozenset({State.PLAYING, State.WORLD_SELECT}),
    State.PLAYING: frozenset({State.PAUSED, State.GAME_OVER, State.LEVEL_COMPLETE}),
    State.PAUSED: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.GAME_OVER: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.LEVEL_COMPLETE: frozenset({State.PLAYING, State.MAIN_MENU}),
}


class InvalidTransitionError(Exception):
    def __init__(self, current: State, target: State) -> None:
        super().__init__(f"cannot go from {current.name} to {target.name}")


class StateMachine:
    def __init__(
        self,
        initial: State = State.MAIN_MENU,
        on_change: Callable[[State, State], None] | None = None,
    ) -> None:
        self.state = initial
        self.on_change = on_change

    def can_transition(self, target: State) -> bool:
        return target in TRANSITIONS[self.state]

    def transition(self, target: State) -> None:
        if not self.can_transition(target):
            raise InvalidTransitionError(self.state, target)
        previous, self.state = self.state, target
        if self.on_change:
            self.on_change(previous, target)
