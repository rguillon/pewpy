"""Putting a song together from its plan: its sections and their parts, or a jingle."""

import random
from collections.abc import Iterator

from pewpewdev.tools.songs.band import (
    BASS,
    CRASH,
    KICK,
    LEAD,
    PROGRAMS,
    SNARE,
    TOMS,
    VOLUMES,
)
from pewpewdev.tools.songs.harmony import MINOR, NOTES
from pewpewdev.tools.songs.plans import Plan
from pewpewdev.tools.songs.tracks.arpeggio import arp
from pewpewdev.tools.songs.tracks.bass import bass
from pewpewdev.tools.songs.tracks.brass import brass
from pewpewdev.tools.songs.tracks.drums import drums
from pewpewdev.tools.songs.tracks.pad import pad
from pewpewdev.tools.songs.tracks.tune import tune
from pewpewdev.tools.songs.writer import Writer, near
from pewpy.audio.midi import DRUMS, Song


def sections(plan: Plan) -> Iterator[tuple[str, int, int]]:
    """(name, first bar, bars) for every section."""
    bar = 0
    for name, bars in plan.sections:
        yield name, bar, bars
        bar += bars


def compose(plan: Plan, seed: int | None = None) -> Song:
    rng = random.Random(plan.seed if seed is None else seed * 100 + plan.seed)  # noqa: S311 - tunes, not cryptography
    writer = Writer(plan, rng, NOTES[plan.key])
    writer.last_tune = near(writer.tonic, 76)
    if plan.jingle:
        return jingle(writer)
    progression = [writer.chord(name) for name in plan.progression]
    for name, first, bars in sections(plan):
        start = first * 4.0
        chords = [progression[(bar // plan.bars_per_chord) % len(progression)] for bar in range(bars)]
        for bar in range(0, bars, plan.bars_per_chord):
            root, shape = chords[bar]
            length = min(plan.bars_per_chord, bars - bar)
            at = start + bar * 4
            pad(writer, at, length, root, shape, 70 if name in ("intro", "break") else 84)
            arp(writer, at, length, root, shape, 52 if name == "intro" else 66)
            if name in ("verse", "chorus"):
                bass(writer, at, length, root)
            if name == "chorus" and plan.brass:
                brass(writer, at, length, root, shape)
        if name == "break":
            bass(writer, start + (bars - 1) * 4, 1, chords[-1][0])  # the bass comes back for the last bar
        if name in ("verse", "chorus"):
            drums(writer, start, bars, busy=name == "chorus", fill=True, crash=True)
        elif name == "break":
            drums(writer, start + (bars - 1) * 4, 1, busy=False, fill=True, crash=False)
        else:
            writer.add(DRUMS, start + bars * 4 - 1, 1, TOMS[0], 80)  # into the verse
        if name == "chorus":
            per_chord = [(chords[bar][0], chords[bar][1]) for bar in range(0, bars, plan.bars_per_chord)]
            tune(writer, start, per_chord, plan.bars_per_chord)
    total = sum(bars for _, bars in plan.sections)
    return song_of(plan, writer, total * 4.0)


def jingle(writer: Writer) -> Song:
    plan = writer.plan
    progression = [writer.chord(name) for name in plan.progression]
    win = plan.jingle == "win"
    for bar, (root, shape) in enumerate(progression):
        at = bar * 4.0
        pad(writer, at, 1 if bar < len(progression) - 1 else 2, root, shape, 90)
        bass = near(root, 40)
        if win:
            writer.add(BASS, at, 3.9 if bar == len(progression) - 1 else 1.9, bass, 110)
            if bar < len(progression) - 1:
                writer.add(BASS, at + 2, 1.9, bass, 100)
            tones = [near(root, 72) + step for step in shape]  # the lead climbs the chord
            for index, step in enumerate((*tones, tones[0] + 12)):
                last = bar == len(progression) - 1 and index == 3
                writer.add(LEAD, at + index * 0.5, 4 if last else 0.45, step, 110)
            writer.add(DRUMS, at, 0.5, CRASH if bar == len(progression) - 1 else KICK, 115)
            writer.add(DRUMS, at + 1, 0.25, SNARE, 110)
            writer.add(DRUMS, at + 3, 0.25, SNARE, 110)
        else:
            writer.add(BASS, at, 3.9, bass, 100)
            tone = near(root + shape[1], 74 - bar * 2)  # the lead sinks
            writer.add(LEAD, at, 1.5, tone, 100)
            writer.add(LEAD, at + 1.5, 2.4, tone - (1 if (tone - writer.tonic) % 12 in MINOR else 2), 90)
            writer.add(DRUMS, at, 1, TOMS[min(bar + 2, 5)], 100)
    end = len(progression) * 4.0 + (4.0 if win else 0.0)
    if not win:
        writer.add(DRUMS, end - 4, 2, TOMS[5], 110)
        writer.add(DRUMS, end - 4, 2, CRASH, 90)
    return song_of(plan, writer, end)


def song_of(plan: Plan, writer: Writer, beats: float) -> Song:
    channels = {note.channel for note in writer.notes}
    return Song(
        tempo=plan.tempo,
        notes=sorted(writer.notes, key=lambda note: (note.start, note.channel, note.pitch)),
        programs={channel: program for channel, program in PROGRAMS.items() if channel in channels},
        volumes={channel: volume for channel, volume in VOLUMES.items() if channel in channels},
        length=beats,
    )
