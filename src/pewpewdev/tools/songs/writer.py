"""A song being written, and voicing its chords."""

import random
from dataclasses import dataclass, field

from pewpewdev.tools.songs.harmony import CHORDS, MINOR
from pewpewdev.tools.songs.plans import Plan
from pewpy.audio.midi import Note


@dataclass
class Writer:
    """A song being written, bar by bar."""

    plan: Plan
    rng: random.Random
    tonic: int
    notes: list[Note] = field(default_factory=list)
    voicing: tuple[int, ...] = ()
    last_tune: int = 0

    def add(self, channel: int, start: float, length: float, pitch: int, velocity: int) -> None:
        self.notes.append(Note(start, length, pitch, max(1, min(127, velocity)), channel))

    def chord(self, name: str) -> tuple[int, tuple[int, ...]]:
        root, shape = CHORDS[name]
        return (self.tonic + root) % 12, shape

    def scale(self) -> list[int]:
        return [pitch for pitch in range(48, 97) if (pitch - self.tonic) % 12 in MINOR]


def near(pitch_class: int, around: int) -> int:
    """The `pitch_class` note nearest `around`."""
    return around + ((pitch_class - around + 6) % 12) - 6


def voice(writer: Writer, root: int, shape: tuple[int, ...]) -> tuple[int, ...]:
    """The chord's notes for the pad, each moving as little as possible from the last chord (around middle C)."""
    classes = [(root + step) % 12 for step in shape]
    if not writer.voicing:
        bottom = near(root, 55)
        return tuple(sorted(bottom + ((pc - root) % 12) for pc in classes))
    previous = writer.voicing
    center = sum(previous) / len(previous)
    best: tuple[int, ...] = ()
    best_cost = 1e9
    for inversion in range(len(classes)):
        order = classes[inversion:] + classes[:inversion]
        bottom = near(order[0], round(center) - 5)
        notes = [bottom]
        for pc in order[1:]:
            notes.append(notes[-1] + ((pc - notes[-1]) % 12 or 12))
        cost = abs(sum(notes) / len(notes) - center) + (0 if 50 <= notes[0] <= 62 else 12)
        if cost < best_cost:
            best, best_cost = tuple(notes), cost
    return best
