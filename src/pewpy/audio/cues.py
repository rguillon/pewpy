"""What to hear when: the sound for each game event, the song for each screen. No Panda3D.

Songs are named after their files in music/ (see pewpy/makers/songs/): "title" on the menus, "world_1"... for each
world's levels, "boss" while a boss is fought (from when it comes until the level ends), and two jingles, played
once: "level_complete" and "game_over".
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum

from pewpy.game.events import Event
from pewpy.game.states import State

SMALL_EXPLOSION = 0.12  # explosions this big or more sound bigger (world units)
BIG_EXPLOSION = 0.4
MIN_GAP = 0.05  # seconds: the same sound isn't started again sooner (many hits in a frame make one sound)
# The events whose sound depends only on their kind.
SOUNDS = {"blast": "blast", "hurt": "hurt", "zap": "zap", "disarmed": "disarmed", "boss": "alarm"}
MIN_GAPS = {"hit": 0.07, "explosion_big": 0.4, "alarm": 2.0}


def event_sound(event: Event) -> str | None:
    """Return the sound for a game event, if it has one (the laser's "burn" doesn't: the laser hums while it fires)."""
    kind = event.kind
    if kind == "shot":
        return "missile" if event.source == "missiles" else "shot"
    if kind == "impact":
        return "hit" if event.source == "enemy" else None  # the player's hits sound as "hurt"
    if kind == "explosion":
        return _explosion_sound(event)
    if kind == "pickup":
        return {"repair": "repair", "life": "extra_life"}.get(event.source, "pickup")
    return SOUNDS.get(kind)


def _explosion_sound(event: Event) -> str:
    if event.source == "Player":
        return "player_explosion"
    if event.size >= BIG_EXPLOSION:
        return "explosion_big"
    return "explosion" if event.size >= SMALL_EXPLOSION else "explosion_small"


def event_sounds(events: Iterable[Event]) -> list[str]:
    """Each sound once, in the order of the events."""
    sounds: list[str] = []
    for event in events:
        sound = event_sound(event)
        if sound is not None and sound not in sounds:
            sounds.append(sound)
    return sounds


@dataclass
class Throttle:
    """Keeps a sound from starting again too soon after itself."""

    time: float = 0.0
    last: dict[str, float] = field(default_factory=dict)

    def update(self, dt: float) -> None:
        """Move the throttle's clock on."""
        self.time += dt

    def allow(self, sound: str) -> bool:
        """Tell whether `sound` may play now (not too soon after the last time); if so, it counts as played."""
        gap = MIN_GAPS.get(sound, MIN_GAP)
        if self.time - self.last.get(sound, -1e9) < gap:
            return False
        self.last[sound] = self.time
        return True


@dataclass(frozen=True)
class Music:
    """A song, and whether it loops."""

    song: str
    loop: bool = True


MENU_MUSIC = Music("title")


def music(state: Enum, world: int, boss: bool) -> Music:
    """Return the song for a screen.

    `world` is the world being played (0 for the first), `boss` whether a boss is being fought (or was just beaten).
    """
    if state is State.LEVEL_COMPLETE:
        return Music("level_complete", loop=False)
    if state is State.GAME_OVER:
        return Music("game_over", loop=False)
    if state in (State.PLAYING, State.PAUSED, State.AI_PLAYING):
        return Music("boss") if boss else Music(f"world_{world + 1}")
    return MENU_MUSIC
