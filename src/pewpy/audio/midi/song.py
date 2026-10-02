"""A song: its notes, its channels' instruments and volumes, its tempo."""

from dataclasses import dataclass, field

DRUMS = 9  # the General MIDI drum channel
TICKS_PER_BEAT = 480


@dataclass(frozen=True)
class Note:
    start: float  # beats
    length: float  # beats
    pitch: int  # MIDI note number, 60 = middle C
    velocity: int = 100  # 1 to 127
    channel: int = 0


@dataclass
class Song:
    tempo: float  # beats per minute
    notes: list[Note] = field(default_factory=list)
    programs: dict[int, int] = field(default_factory=dict)  # channel -> General MIDI program (0 to 127)
    volumes: dict[int, int] = field(default_factory=dict)  # channel -> volume (0 to 127, 100 when unset)
    tempo_changes: list[tuple[float, float]] = field(default_factory=list)  # (beat, bpm) after the start
    length: float = 0.0  # beats; the song loops from here (0: the end of its last note)

    @property
    def beats(self) -> float:
        return self.length or max((note.start + note.length for note in self.notes), default=0.0)

    def seconds(self, beat: float) -> float:
        """When `beat` is played, with the tempo changes."""
        time, at, tempo = 0.0, 0.0, self.tempo
        for change_beat, bpm in sorted(self.tempo_changes):
            if change_beat >= beat:
                break
            time += (change_beat - at) * 60.0 / tempo
            at, tempo = change_beat, bpm
        return time + (beat - at) * 60.0 / tempo

    @property
    def duration(self) -> float:
        """Seconds."""
        return self.seconds(self.beats)


class MidiError(ValueError):
    @classmethod
    def not_midi(cls) -> "MidiError":
        return cls("not a standard MIDI file")

    @classmethod
    def truncated(cls) -> "MidiError":
        return cls("the MIDI file ends too soon")

    @classmethod
    def smpte(cls) -> "MidiError":
        return cls("SMPTE timing isn't supported, only ticks per beat")
