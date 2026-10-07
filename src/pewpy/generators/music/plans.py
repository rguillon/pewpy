"""Every song's plan: its key, tempo, chords, seed and style."""

import random
from dataclasses import dataclass, replace

from pewpy.generators.music.harmony import ARPS, NOTES


@dataclass(frozen=True)
class Plan:
    """What a song is to be: its key, tempo, chords and how each instrument plays."""

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

PROGRESSIONS = (  # the chords a new song picks from: every song's, and a few more
    *dict.fromkeys(plan.progression for plan in PLANS if not plan.jingle),
    ("i", "iv", "VI", "V"),
    ("i", "VII", "VImaj7", "VII"),
    ("i", "III", "VII", "iv7"),
    ("VImaj7", "i", "VII", "V"),
)
DRUM_STYLES = ("half", "standard", "four")
BASS_STYLES = ("eighths", "gallop", "sixteenths")
TEMPO_CHANGE = 0.1  # a new song's tempo is within this share of its plan's
BRASS_SHARE = 0.4  # of the new songs with brass on the chorus


def vary(plan: Plan, seed: int) -> Plan:
    """Return a new song's plan from a song's: another key and tempo; another progression and arrangement (drums,
    bass, arpeggio, brass) unless it's a jingle, whose chords make it a win or a loss."""  # noqa: D205, D209 - two lines
    rng = random.Random(seed)
    key = rng.choice(list(NOTES))
    tempo = round(plan.tempo * rng.uniform(1 - TEMPO_CHANGE, 1 + TEMPO_CHANGE))
    if plan.jingle:
        return replace(plan, key=key, tempo=tempo)
    return replace(
        plan,
        key=key,
        tempo=tempo,
        progression=rng.choice(PROGRESSIONS),
        drums=rng.choice(DRUM_STYLES),
        bass=rng.choice(BASS_STYLES),
        arp=rng.choice(list(ARPS)),
        brass=rng.random() < BRASS_SHARE,
    )


def describe(plan: Plan) -> str:
    """Return a song's title in its MIDI file, with its key and chords: "Neon Horizon | A minor | i VImaj7 III VII"."""
    return f"{plan.title} | {plan.key} minor | {' '.join(plan.progression)}"
