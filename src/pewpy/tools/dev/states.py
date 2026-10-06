"""The dev tools' screens, on top of the game's states (pewpy.game.states).

Each opens from the main menu and goes back to it.
"""

from enum import Enum, auto

from pewpy.game.states import TRANSITIONS, State, Transitions


class DevState(Enum):
    """The dev tools' screens."""

    MODELS = auto()  # every ship and pickup on show, for working on the models
    BOSSES = auto()  # every boss on show, a world per page
    CANDIDATES = auto()  # numbered model candidates for new enemies (models/candidates/enemies), to pick from
    PLAYER_CANDIDATES = auto()  # the same for new player ships (models/candidates/player)
    BOSS_CANDIDATES = auto()  # the same for new bosses (models/candidates/bosses)
    PROP_CANDIDATES = auto()  # numbered prop candidates for the grounds (props/candidates), to pick from
    BACKGROUND_CANDIDATES = auto()  # numbered background candidates (models/candidates/backgrounds), to pick from
    AI_LEARNING = auto()  # the AI learns to play, in the background, while one of its brains plays on screen
    AI_RATING = auto()  # the trained AI rates every level for every ship
    AI_PLAYING = auto()  # the trained AI plays the game from the ship and level picked, to watch it


DEV_TRANSITIONS: Transitions = {
    **TRANSITIONS,
    State.MAIN_MENU: TRANSITIONS[State.MAIN_MENU] | frozenset(DevState),
    State.LEVEL_SELECT: TRANSITIONS[State.LEVEL_SELECT] | {DevState.AI_PLAYING},  # the level the AI plays picked
    **{screen: frozenset({State.MAIN_MENU}) for screen in DevState},
    DevState.AI_PLAYING: frozenset({State.MAIN_MENU, State.LEVEL_SELECT}),  # Escape: pick another level
}
