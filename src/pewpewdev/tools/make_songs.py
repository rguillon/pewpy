"""Generate the game's synthwave songs as MIDI files (data/music/).

    make songs                               # every song, each from its own seed: the same songs every time
    make songs ARGS="--seed 1234"            # new songs: the same plans (keys, tempos, chords), new tunes
    make songs ARGS="--only boss world_2"    # just these
    make songs ARGS="--wav"                  # also build/music/<name>.wav, as the game plays it, to listen to

(or `uv run python -m pewpewdev.tools.make_songs ...`). The .mid files open in any MIDI player or music program (General
MIDI: synth bass, warm pad, square arpeggio, saw lead, brass, drums on channel 10); the game plays them with its own
synthesizer (src/pewpy/audio/synth.py). A song's own .mid can replace a generated one: the game reads any MIDI file.

Every song is the same recipe, in a minor key: a chord progression, a bar per chord (two when slow); sections in
turn (an intro, a verse with the drums, bass and arpeggio, a chorus with the lead tune, a breakdown, the chorus
again), a tom fill closing each, a crash opening the next. The tune is a two-bar motif, repeated and varied, chord
notes on the beats and scale steps between. Songs loop (a "loop" marker where they end); the two jingles don't.
"""

import argparse
import random
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from pewpewdev.paths import BUILD, DATA
from pewpy.audio import midi, synth
from pewpy.audio.midi import DRUMS, Note, Song

OUT = DATA / "music"
PREVIEWS = BUILD / "music"

BASS, PAD, ARP, LEAD, BRASS = 0, 1, 2, 3, 4  # channels
PROGRAMS = {BASS: 38, PAD: 89, ARP: 80, LEAD: 81, BRASS: 61}  # synth bass 1, warm pad, square, saw lead, brass
VOLUMES = {BASS: 100, PAD: 90, ARP: 80, LEAD: 105, BRASS: 95, DRUMS: 110}
KICK, SNARE, CLAP, CLOSED_HAT, OPEN_HAT, CRASH = 36, 38, 39, 42, 46, 49
TOMS = (50, 48, 47, 45, 43, 41)  # high to low

MINOR = (0, 2, 3, 5, 7, 8, 10)
CHORDS = {  # name -> (root, from the key's tonic; the chord's notes, from its root)
    "i": (0, (0, 3, 7)),
    "i7": (0, (0, 3, 7, 10)),
    "bII": (1, (0, 4, 7)),
    "III": (3, (0, 4, 7)),
    "IIImaj7": (3, (0, 4, 7, 11)),
    "iv": (5, (0, 3, 7)),
    "iv7": (5, (0, 3, 7, 10)),
    "v": (7, (0, 3, 7)),
    "V": (7, (0, 4, 7)),
    "VI": (8, (0, 4, 7)),
    "VImaj7": (8, (0, 4, 7, 11)),
    "VII": (10, (0, 4, 7)),
    "I": (0, (0, 4, 7)),
}
NOTES = {"C": 0, "C#": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}

RHYTHMS = (  # a bar of the tune: (start, length) in beats
    ((0, 1.5), (1.5, 0.5), (2, 1), (3, 1)),
    ((0, 0.5), (0.5, 0.5), (1, 1), (2, 1.5), (3.5, 0.5)),
    ((0, 2), (2, 1), (3, 1)),
    ((0, 1), (1, 0.5), (1.5, 1.5), (3, 0.5), (3.5, 0.5)),
    ((0.5, 0.5), (1, 0.5), (1.5, 1.5), (3, 1)),
    ((0, 0.75), (0.75, 0.75), (1.5, 0.5), (2, 2)),
)
ARPS = {
    "up": (0, 1, 2, 3),
    "updown": (0, 1, 2, 3, 2, 1),
    "broken": (0, 2, 1, 3),
    "pedal": (0, 1, 0, 2, 0, 3, 0, 2),
}


@dataclass(frozen=True)
class Plan:
    name: str  # the file's name
    title: str  # in the MIDI file
    key: str
    tempo: float
    progression: tuple[str, ...]
    seed: int
    bars_per_chord: int = 1
    drums: str = "standard"  # "half" (kick on 1, snare on 3), "standard" (snare on 2 and 4), "four" (kick every beat)
    bass: str = "eighths"  # "eighths", "gallop", "sixteenths"
    arp: str = "up"
    brass: bool = False  # stabs on the chorus
    sections: tuple[tuple[str, int], ...] = (("intro", 4), ("verse", 8), ("chorus", 8), ("break", 4), ("chorus", 8))
    jingle: str = ""  # "win" or "lose": a short tune played once instead


PLANS = (
    Plan("title", "Neon Horizon", "A", 96, ("i", "VImaj7", "III", "VII"), 11, arp="updown"),
    Plan("world_1", "Starlit Orbit", "E", 104, ("i", "VI", "VII", "i"), 21, arp="broken"),
    Plan("world_2", "Midnight Heartland", "D", 100, ("VImaj7", "VII", "i", "i7"), 31, drums="half", bass="gallop"),
    Plan(
        "world_3", "Chrome Tides", "F#", 90, ("i", "iv", "VImaj7", "V"), 41, bars_per_chord=1, arp="pedal", drums="half"
    ),
    Plan("world_4", "Dust and Lasers", "C", 112, ("i", "VII", "VI", "VII"), 51, bass="gallop", brass=True),
    Plan(
        "world_5", "Grid Runner", "G", 120, ("i", "VI", "iv7", "V"), 61, drums="four", bass="sixteenths", arp="broken"
    ),
    Plan("world_6", "Red Rock Run", "A", 108, ("i", "VII", "VI", "V"), 71, bass="gallop", arp="updown"),
    Plan("world_7", "Furnace Heart", "B", 116, ("i", "iv", "VII", "III"), 81, drums="four", brass=True),
    Plan(
        "world_8",
        "Neon Skyline",
        "E",
        124,
        ("i", "VI", "III", "VII"),
        91,
        drums="four",
        bass="sixteenths",
        arp="broken",
    ),
    Plan(
        "boss",
        "Overdrive",
        "B",
        132,
        ("i", "bII", "i", "VII"),
        71,
        drums="four",
        bass="sixteenths",
        brass=True,
        sections=(("intro", 2), ("verse", 8), ("chorus", 8), ("break", 4), ("chorus", 8)),
    ),
    Plan("level_complete", "Sector Clear", "A", 116, ("VI", "VII", "I"), 81, jingle="win"),
    Plan("game_over", "Signal Lost", "D", 72, ("i", "iv", "VI", "V"), 91, jingle="lose"),
)


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


def _near(pitch_class: int, around: int) -> int:
    """The `pitch_class` note nearest `around`."""
    return around + ((pitch_class - around + 6) % 12) - 6


def _voice(writer: Writer, root: int, shape: tuple[int, ...]) -> tuple[int, ...]:
    """The chord's notes for the pad, each moving as little as possible from the last chord (around middle C)."""
    classes = [(root + step) % 12 for step in shape]
    if not writer.voicing:
        bottom = _near(root, 55)
        return tuple(sorted(bottom + ((pc - root) % 12) for pc in classes))
    previous = writer.voicing
    center = sum(previous) / len(previous)
    best: tuple[int, ...] = ()
    best_cost = 1e9
    for inversion in range(len(classes)):
        order = classes[inversion:] + classes[:inversion]
        bottom = _near(order[0], round(center) - 5)
        notes = [bottom]
        for pc in order[1:]:
            notes.append(notes[-1] + ((pc - notes[-1]) % 12 or 12))
        cost = abs(sum(notes) / len(notes) - center) + (0 if 50 <= notes[0] <= 62 else 12)
        if cost < best_cost:
            best, best_cost = tuple(notes), cost
    return best


def _pad(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...], velocity: int) -> None:
    writer.voicing = _voice(writer, root, shape)
    for pitch in writer.voicing:
        writer.add(PAD, start, bars * 4 - 0.05, pitch, velocity)


def _bass(writer: Writer, start: float, bars: int, root: int) -> None:
    low = _near(root, 38)
    style = writer.plan.bass
    for bar in range(bars):
        at = start + bar * 4
        last = bar == bars - 1
        if style == "sixteenths":
            for step in range(16):
                octave = 12 if step % 8 == 6 else 0
                writer.add(BASS, at + step / 4, 0.22, low + octave, 112 if step % 4 == 0 else 88)
        elif style == "gallop":
            for beat in range(4):
                for offset, length in ((0, 0.5), (0.5, 0.25), (0.75, 0.25)):
                    up = 12 if (beat == 3 and offset == 0.5 and last) else 0
                    writer.add(BASS, at + beat + offset, length * 0.9, low + up, 110 if offset == 0 else 85)
        else:
            for step in range(8):
                up = 12 if step in (3, 7) else 0
                writer.add(BASS, at + step / 2, 0.42, low + up, 112 if step % 2 == 0 else 92)


def _arp(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...], velocity: int) -> None:
    tones = [_near(root, 64) + step for step in shape[:3]]
    tones.append(tones[0] + 12)
    pattern = ARPS[writer.plan.arp]
    for step in range(bars * 16):
        lift = 12 if (step // 16) % 2 and writer.plan.arp != "pedal" else 0
        accent = 18 if step % 4 == 0 else 0
        writer.add(ARP, start + step / 4, 0.2, tones[pattern[step % len(pattern)]] + lift, velocity + accent)


def _hats(writer: Writer, at: float, busy: bool, until: float) -> None:
    style = writer.plan.drums
    count = 16 if busy and style != "half" else 8
    for step in range(count):
        when = step * 4 / count
        if when >= until:
            break
        open_hat = style == "four" and when % 1 == 0.5
        writer.add(DRUMS, at + when, 0.1, OPEN_HAT if open_hat else CLOSED_HAT, 80 if when % 1 == 0 else 58)


def _drums(writer: Writer, start: float, bars: int, busy: bool, fill: bool, crash: bool) -> None:
    style = writer.plan.drums
    kicks = {"half": (0, 2.5), "standard": (0, 1.5, 2), "four": (0, 1, 2, 3)}[style]
    snares = (2,) if style == "half" else (1, 3)
    if crash:
        writer.add(DRUMS, start, 0.5, CRASH, 105)
    for bar in range(bars):
        at = start + bar * 4
        until = 2 if fill and bar == bars - 1 else 4  # the fill takes the last two beats
        for beat in kicks:
            if beat < until:
                writer.add(DRUMS, at + beat, 0.25, KICK, 120 if beat == 0 else 108)
        for beat in snares:
            if beat < until:
                writer.add(DRUMS, at + beat, 0.25, SNARE, 118)
        _hats(writer, at, busy, until)
        if until == 2:  # down the toms, two hits each
            for step in range(8):
                writer.add(DRUMS, at + 2 + step / 4, 0.25, TOMS[min(step // 2 + step % 2, 5)], 96 + step * 3)


def _brass(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...]) -> None:
    for bar in range(bars):
        for beat, length in ((0, 0.4), (1.5, 0.4), (3, 0.9)) if bar % 2 == 0 else ((0, 0.4), (2.5, 1.3)):
            for step in shape[:3]:
                writer.add(BRASS, start + bar * 4 + beat, length, _near(root, 60) + step, 104)


def _tune_pitch(writer: Writer, chord_tones: set[int], on_beat: bool) -> int:
    """The next note of the tune: a chord note near the last one on the beat, else a step along the scale."""
    previous = writer.last_tune
    scale = writer.scale()
    candidates = [pitch for pitch in scale if 67 <= pitch <= 86]
    if on_beat:
        choices = [pitch for pitch in candidates if pitch % 12 in chord_tones and abs(pitch - previous) <= 7]
        choices = choices or [pitch for pitch in candidates if pitch % 12 in chord_tones]
        weights = [1.0 / (1 + abs(pitch - previous)) ** 0.7 for pitch in choices]
        return writer.rng.choices(choices, weights)[0]
    index = min(range(len(candidates)), key=lambda i: abs(candidates[i] - previous))
    step = writer.rng.choice((-2, -1, -1, 1, 1, 2))
    return candidates[max(0, min(len(candidates) - 1, index + step))]


def _motif(writer: Writer) -> list[tuple[float, float]]:
    """Two bars of rhythm for the tune, the second ending on a long note."""
    first = writer.rng.choice(RHYTHMS)
    second = writer.rng.choice((((0, 1.5), (1.5, 2.5)), ((0, 0.5), (0.5, 0.5), (1, 3)), ((0, 1), (1, 3))))
    return [*first, *((4 + at, length) for at, length in second)]


def _tune(writer: Writer, start: float, chords: list[tuple[int, tuple[int, ...]]], bars_per_chord: int) -> None:
    """The lead's tune over the chorus: a motif four times, the third varied, the last ending on the tonic."""
    motif = _motif(writer)
    variation = list(writer.rng.choice(RHYTHMS)) + [(4 + at, length) for at, length in motif if at >= 4]
    total_bars = len(chords) * bars_per_chord
    phrases = max(1, total_bars // 2)
    remembered: list[int] = []
    for phrase in range(phrases):
        rhythm = variation if phrase % 4 == 2 else motif
        repeat = phrase % 2 == 1 and remembered and phrase % 4 != 2
        for index, (at, length) in enumerate(rhythm):
            beat = phrase * 8 + at
            root, shape = chords[min(int(beat // (4 * bars_per_chord)), len(chords) - 1)]
            tones = {(root + step) % 12 for step in shape}
            last_note = phrase == phrases - 1 and index == len(rhythm) - 1
            if last_note:
                pitch = _near(writer.tonic, writer.last_tune)
            elif repeat and index < len(remembered) - 2:
                pitch = remembered[index]  # the answer starts like the call
                if pitch % 12 not in tones and at % 1 == 0:
                    pitch = _tune_pitch(writer, tones, on_beat=True)
            else:
                pitch = _tune_pitch(writer, tones, on_beat=at % 1 == 0)
            if phrase % 2 == 0:
                remembered = [*remembered[:index], pitch] if index else [pitch]
            writer.last_tune = pitch
            writer.add(LEAD, start + beat, length * 0.95, pitch, 108 if at % 1 == 0 else 94)


def _sections(plan: Plan) -> Iterator[tuple[str, int, int]]:
    """(name, first bar, bars) for every section."""
    bar = 0
    for name, bars in plan.sections:
        yield name, bar, bars
        bar += bars


def compose(plan: Plan, seed: int | None = None) -> Song:
    rng = random.Random(plan.seed if seed is None else seed * 100 + plan.seed)  # noqa: S311 - tunes, not cryptography
    writer = Writer(plan, rng, NOTES[plan.key])
    writer.last_tune = _near(writer.tonic, 76)
    if plan.jingle:
        return _jingle(writer)
    progression = [writer.chord(name) for name in plan.progression]
    for name, first, bars in _sections(plan):
        start = first * 4.0
        chords = [progression[(bar // plan.bars_per_chord) % len(progression)] for bar in range(bars)]
        for bar in range(0, bars, plan.bars_per_chord):
            root, shape = chords[bar]
            length = min(plan.bars_per_chord, bars - bar)
            at = start + bar * 4
            _pad(writer, at, length, root, shape, 70 if name in ("intro", "break") else 84)
            _arp(writer, at, length, root, shape, 52 if name == "intro" else 66)
            if name in ("verse", "chorus"):
                _bass(writer, at, length, root)
            if name == "chorus" and plan.brass:
                _brass(writer, at, length, root, shape)
        if name == "break":
            _bass(writer, start + (bars - 1) * 4, 1, chords[-1][0])  # the bass comes back for the last bar
        if name in ("verse", "chorus"):
            _drums(writer, start, bars, busy=name == "chorus", fill=True, crash=True)
        elif name == "break":
            _drums(writer, start + (bars - 1) * 4, 1, busy=False, fill=True, crash=False)
        else:
            writer.add(DRUMS, start + bars * 4 - 1, 1, TOMS[0], 80)  # into the verse
        if name == "chorus":
            per_chord = [(chords[bar][0], chords[bar][1]) for bar in range(0, bars, plan.bars_per_chord)]
            _tune(writer, start, per_chord, plan.bars_per_chord)
    total = sum(bars for _, bars in plan.sections)
    return _song(plan, writer, total * 4.0)


def _jingle(writer: Writer) -> Song:
    plan = writer.plan
    progression = [writer.chord(name) for name in plan.progression]
    win = plan.jingle == "win"
    for bar, (root, shape) in enumerate(progression):
        at = bar * 4.0
        _pad(writer, at, 1 if bar < len(progression) - 1 else 2, root, shape, 90)
        bass = _near(root, 40)
        if win:
            writer.add(BASS, at, 3.9 if bar == len(progression) - 1 else 1.9, bass, 110)
            if bar < len(progression) - 1:
                writer.add(BASS, at + 2, 1.9, bass, 100)
            tones = [_near(root, 72) + step for step in shape]  # the lead climbs the chord
            for index, step in enumerate((*tones, tones[0] + 12)):
                last = bar == len(progression) - 1 and index == 3
                writer.add(LEAD, at + index * 0.5, 4 if last else 0.45, step, 110)
            writer.add(DRUMS, at, 0.5, CRASH if bar == len(progression) - 1 else KICK, 115)
            writer.add(DRUMS, at + 1, 0.25, SNARE, 110)
            writer.add(DRUMS, at + 3, 0.25, SNARE, 110)
        else:
            writer.add(BASS, at, 3.9, bass, 100)
            tone = _near(root + shape[1], 74 - bar * 2)  # the lead sinks
            writer.add(LEAD, at, 1.5, tone, 100)
            writer.add(LEAD, at + 1.5, 2.4, tone - (1 if (tone - writer.tonic) % 12 in MINOR else 2), 90)
            writer.add(DRUMS, at, 1, TOMS[min(bar + 2, 5)], 100)
    end = len(progression) * 4.0 + (4.0 if win else 0.0)
    if not win:
        writer.add(DRUMS, end - 4, 2, TOMS[5], 110)
        writer.add(DRUMS, end - 4, 2, CRASH, 90)
    return _song(plan, writer, end)


def _song(plan: Plan, writer: Writer, beats: float) -> Song:
    channels = {note.channel for note in writer.notes}
    return Song(
        tempo=plan.tempo,
        notes=sorted(writer.notes, key=lambda note: (note.start, note.channel, note.pitch)),
        programs={channel: program for channel, program in PROGRAMS.items() if channel in channels},
        volumes={channel: volume for channel, volume in VOLUMES.items() if channel in channels},
        length=beats,
    )


def write(plan: Plan, out: Path, seed: int | None = None, wav: Path | None = None) -> Path:
    song = compose(plan, seed)
    path = out / f"{plan.name}.mid"
    path.write_bytes(midi.write(song, plan.title))
    if wav is not None:
        wav.mkdir(parents=True, exist_ok=True)
        samples = synth.render(midi.read(path.read_bytes()), loop=not plan.jingle)
        (wav / f"{plan.name}.wav").write_bytes(synth.wav_bytes(samples))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, help="new tunes from this seed (default: each song's own)")
    parser.add_argument("--only", nargs="+", choices=[plan.name for plan in PLANS], help="just these songs")
    parser.add_argument("--out", type=Path, default=OUT, help="where (default: the game's music)")
    parser.add_argument("--wav", action="store_true", help=f"also render them to {PREVIEWS}")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for plan in PLANS:
        if args.only and plan.name not in args.only:
            continue
        path = write(plan, args.out, args.seed, PREVIEWS if args.wav else None)
        song = midi.read(path.read_bytes())
        print(f"{plan.name}: {plan.title!r}, {plan.key} minor, {plan.tempo:g} bpm, {song.duration:.0f} s -> {path}")


if __name__ == "__main__":
    main()
