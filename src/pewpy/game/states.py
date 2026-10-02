"""Global game state machine (01-gameplay.md, "Global state")."""

from collections.abc import Callable, Mapping
from enum import Enum, auto


class State(Enum):
    MAIN_MENU = auto()
    SHIP_SELECT = auto()  # picking the player's ship, before the world
    WORLD_SELECT = auto()
    LEVEL_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()


# Where each state can go. The states are any Enum's members: the dev tools (pewpewdev) add screens of their own.
Transitions = Mapping[Enum, frozenset[Enum]]
TRANSITIONS: Transitions = {
    State.MAIN_MENU: frozenset({State.SHIP_SELECT}),
    State.SHIP_SELECT: frozenset({State.WORLD_SELECT, State.MAIN_MENU}),
    State.WORLD_SELECT: frozenset({State.LEVEL_SELECT, State.SHIP_SELECT}),
    State.LEVEL_SELECT: frozenset({State.PLAYING, State.WORLD_SELECT}),
    State.PLAYING: frozenset({State.PAUSED, State.GAME_OVER, State.LEVEL_COMPLETE}),
    State.PAUSED: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.GAME_OVER: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.LEVEL_COMPLETE: frozenset({State.PLAYING, State.MAIN_MENU}),
}


class InvalidTransitionError(Exception):
    def __init__(self, current: Enum, target: Enum) -> None:
        super().__init__(f"cannot go from {current.name} to {target.name}")


class StateMachine:
    def __init__(
        self,
        initial: Enum = State.MAIN_MENU,
        on_change: Callable[[Enum, Enum], None] | None = None,
        transitions: Transitions = TRANSITIONS,
    ) -> None:
        self.state = initial
        self.on_change = on_change
        self.transitions = transitions

    def can_transition(self, target: Enum) -> bool:
        return target in self.transitions[self.state]

    def transition(self, target: Enum) -> None:
        if not self.can_transition(target):
            raise InvalidTransitionError(self.state, target)
        previous, self.state = self.state, target
        if self.on_change:
            self.on_change(previous, target)
