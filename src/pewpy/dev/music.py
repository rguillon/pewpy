"""The music browser of the Dev menu: the game's songs, one at a time, to make new ones in their place.

Left and Right go from one song to the next (it plays), Space composes a new one from the song's plan, varied (another
key, tempo, chords and arrangement, new tunes; it plays, not saved), Enter saves it in place of the song's MIDI file
(data/music/). Independent from playing: the app plays `music`.
"""

import random
from dataclasses import dataclass, field
from pathlib import Path

from pewpy.audio import midi
from pewpy.audio.cues import Music
from pewpy.data import data_folder
from pewpy.makers.songs.compose import midi_file
from pewpy.makers.songs.plans import PLANS, Plan, describe

MUSIC_FOLDER = "music"  # data/music/<name>.mid
SEEDS = 1_000_000  # a new song's seed is below this
NEW_PREFIX = "new-"  # a new song's name in the music library, never a song's file


def song_path(name: str) -> Path:
    """Return the file of a song, in data/music/."""
    return Path(str(data_folder() / MUSIC_FOLDER)) / f"{name}.mid"


@dataclass
class MusicBrowser:
    """The songs (their plans, see pewpy.makers.songs.plans), the one on show, and the new song made for it."""

    rng: random.Random = field(default_factory=random.Random)
    index: int = 0
    seed: int | None = None  # the new song's: None while there's none
    new: bytes | None = None  # the new song's MIDI file, not saved
    saved: bool = False  # just saved

    @property
    def plan(self) -> Plan:
        """Return the song on show's plan."""
        return PLANS[self.index]

    def move(self, step: int) -> None:
        """Show the next song (step 1) or the previous one (-1), wrapping around; a new song not saved is lost."""
        self.index = (self.index + step) % len(PLANS)
        self.seed = self.new = None
        self.saved = False

    def generate(self) -> bytes:
        """Compose a new song from the plan, with new tunes; return its MIDI file."""
        self.seed = self.rng.randrange(SEEDS)
        self.new = midi_file(self.plan, self.seed)
        self.saved = False
        return self.new

    def save(self) -> None:
        """Save the new song in place of the one on show (nothing to do without one)."""
        if self.new is None:
            return
        path = song_path(self.plan.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.new)
        self.saved = True

    def name(self) -> str:
        """Return the name the song on show plays under: its own, or the new song's."""
        return self.plan.name if self.seed is None else f"{NEW_PREFIX}{self.plan.name}-{self.seed}"

    def music(self) -> Music:
        """Return the song on show to play (the new one, if any; a jingle once)."""
        return Music(self.name(), loop=not self.plan.jingle)

    def data(self) -> bytes | None:
        """Return the song on show's MIDI file (None if it has none yet)."""
        if self.new is not None:
            return self.new
        path = song_path(self.plan.name)
        return path.read_bytes() if path.is_file() else None

    def details(self) -> str:
        """Describe the song on show from its MIDI file: its title, key, tempo, length and chords.

        The key and chords are in its title (see pewpy.makers.songs.plans.describe); a file titled otherwise is its
        plan's song.
        """
        plan = self.plan
        kind = "jingle, played once" if plan.jingle else "loops"
        data = self.data()
        if data is None:
            title, key, chords = describe(plan).split(" | ")
            return f'"{title}": {key}, {plan.tempo:g} bpm, no file yet ({kind}). Chords: {chords}'
        song = midi.read(data)
        parts = song.title.split(" | ")
        title, key, chords = parts if len(parts) == 3 else describe(plan).split(" | ")
        return f'"{title}": {key}, {song.tempo:.0f} bpm, {song.duration:.0f} s ({kind}). Chords: {chords}'
