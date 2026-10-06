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
    AI_LEARNING = auto()  # the AI learns to play, in the background, while one of its brains plays on screen
    AI_RATING = auto()  # the trained AI rates every level for every ship
    AI_PLAYING = auto()  # the trained AI plays the game, to watch it


DEV_TRANSITIONS: Transitions = {
    **TRANSITIONS,
    State.MAIN_MENU: TRANSITIONS[State.MAIN_MENU] | frozenset(DevState),
    **{screen: frozenset({State.MAIN_MENU}) for screen in DevState},
}
