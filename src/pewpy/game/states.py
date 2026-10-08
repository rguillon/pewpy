"""Global game state machine (01-gameplay.md, "Global state")."""

from collections.abc import Callable, Mapping
from enum import Enum, auto


class State(Enum):
    """The game's screens."""

    MAIN_MENU = auto()
    SHIP_SELECT = auto()  # picking the player's ship, before the world
    WORLD_SELECT = auto()
    LEVEL_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    DEV_MENU = auto()  # the Dev menu: which models and parts to browse
    MODEL_BROWSER = auto()  # browsing a category's models, making new ones (see pewpy.generators.models)
    MUSIC_BROWSER = auto()  # browsing the songs, making new ones (see pewpy.generators.music.browser)
    BACKGROUND_BROWSER = auto()  # background candidates, one theme at a time (see pewpy.generators.backgrounds)
    SCREENSHOTS = auto()  # a level's moment, to save as its world's screenshot (see pewpy.generators.screenshots)
    AI_PLAYING = auto()  # watching the AI play from the ship and level picked in the Dev menu (see pewpy.ai)
    PART_BROWSER = auto()  # browsing the catalog's parts (see pewpy.generators.models.parts)


# Where each state can go.
Transitions = Mapping[Enum, frozenset[Enum]]
TRANSITIONS: Transitions = {
    State.MAIN_MENU: frozenset({State.SHIP_SELECT, State.DEV_MENU}),
    State.SHIP_SELECT: frozenset({State.WORLD_SELECT, State.MAIN_MENU, State.DEV_MENU}),  # Dev: picking for the AI
    State.WORLD_SELECT: frozenset({State.LEVEL_SELECT, State.SHIP_SELECT}),
    State.LEVEL_SELECT: frozenset({State.PLAYING, State.AI_PLAYING, State.WORLD_SELECT}),
    State.PLAYING: frozenset({State.PAUSED, State.GAME_OVER, State.LEVEL_COMPLETE}),
    State.PAUSED: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.GAME_OVER: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.LEVEL_COMPLETE: frozenset({State.PLAYING, State.MAIN_MENU}),
    State.DEV_MENU: frozenset({
        State.MAIN_MENU,
        State.MODEL_BROWSER,
        State.MUSIC_BROWSER,
        State.BACKGROUND_BROWSER,
        State.SHIP_SELECT,
        State.SCREENSHOTS,
        State.PART_BROWSER,
    }),
    State.SCREENSHOTS: frozenset({State.DEV_MENU}),
    State.MODEL_BROWSER: frozenset({State.DEV_MENU}),
    State.MUSIC_BROWSER: frozenset({State.DEV_MENU}),
    State.BACKGROUND_BROWSER: frozenset({State.DEV_MENU}),
    State.AI_PLAYING: frozenset({State.LEVEL_SELECT}),  # Escape: pick another level
    State.PART_BROWSER: frozenset({State.DEV_MENU}),
}


class InvalidTransitionError(Exception):
    """The game can't go from one screen to the other."""

    def __init__(self, current: Enum, target: Enum) -> None:
        """Say the game can't go from the screen `current` to the screen `target`."""
        super().__init__(f"cannot go from {current.name} to {target.name}")


class StateMachine:
    """Which screen the game is on, and where it can go from there."""

    def __init__(
        self,
        initial: Enum = State.MAIN_MENU,
        on_change: Callable[[Enum, Enum], None] | None = None,
        transitions: Transitions = TRANSITIONS,
    ) -> None:
        """Start on `initial`, calling `on_change` at every move (going through `transitions`)."""
        self.state = initial
        self.on_change = on_change
        self.transitions = transitions

    def can_transition(self, target: Enum) -> bool:
        """Tell whether the game can go to `target` from here."""
        return target in self.transitions[self.state]

    def transition(self, target: Enum) -> None:
        """Go to `target` (InvalidTransitionError if it can't), telling `on_change`."""
        if not self.can_transition(target):
            raise InvalidTransitionError(self.state, target)
        previous, self.state = self.state, target
        if self.on_change:
            self.on_change(previous, target)
