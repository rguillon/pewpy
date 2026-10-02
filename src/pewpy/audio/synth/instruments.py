"""The instruments, and which one each General MIDI program plays."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    wave: str = "saw"
    voices: int = 1  # detuned copies (a "supersaw" with more)
    detune: float = 0.0  # cents between the outermost voices
    sub: float = 0.0  # a square an octave below, this loud
    attack: float = 0.005
    decay: float = 0.3
    sustain: float = 0.7
    release: float = 0.15
    cutoff: float = 3000.0  # filter, Hz, once its envelope has decayed
    brightness: float = 2.0  # the filter opens this many times wider at the start of each note
    filter_decay: float = 0.2  # seconds
    vibrato: float = 0.0  # cents
    gain: float = 0.3
    pan: float = 0.0  # -1 left, 1 right
    spread: float = 0.0  # voices spread across the stereo field
    delay: float = 0.0  # send to the stereo delay
    reverb: float = 0.2  # send to the reverb
    ducks: bool = False  # ducks under the kick drum


BASS = Instrument(wave="saw", sub=0.6, decay=0.25, sustain=0.6, release=0.05, cutoff=420, brightness=3.0,
                  filter_decay=0.12, gain=0.45, reverb=0.03, ducks=True)  # fmt: skip
PAD = Instrument(wave="saw", voices=5, detune=24, attack=0.5, decay=1.0, sustain=0.85, release=1.2, cutoff=1500,
                 brightness=1.4, filter_decay=1.5, gain=0.13, spread=0.8, reverb=0.5, ducks=True)  # fmt: skip
LEAD = Instrument(wave="saw", voices=3, detune=14, attack=0.01, decay=0.4, sustain=0.75, release=0.25, cutoff=3800,
                  brightness=1.5, vibrato=18, gain=0.2, spread=0.3, delay=0.35, reverb=0.35)  # fmt: skip
PLUCK = Instrument(wave="square", decay=0.14, sustain=0.0, release=0.08, cutoff=1200, brightness=4.0,
                   filter_decay=0.08, gain=0.17, pan=0.25, delay=0.45, reverb=0.25)  # fmt: skip
KEYS = Instrument(wave="triangle", voices=2, detune=8, decay=0.8, sustain=0.3, release=0.4, cutoff=2500, gain=0.2,
                  spread=0.5, reverb=0.4)  # fmt: skip
BRASS = Instrument(wave="saw", voices=3, detune=10, attack=0.04, decay=0.5, sustain=0.8, release=0.3, cutoff=2200,
                   brightness=1.8, filter_decay=0.3, gain=0.16, spread=0.6, reverb=0.35)  # fmt: skip


def instrument(program: int) -> Instrument:
    """The instrument for a General MIDI program: its family decides."""
    if 32 <= program <= 39:  # basses
        return BASS
    if 88 <= program <= 95 or 48 <= program <= 55:  # pads, strings and choirs
        return PAD
    if program == 80 or 96 <= program <= 103:  # square lead, effects: plucks for arpeggios
        return PLUCK
    if 81 <= program <= 87:  # leads
        return LEAD
    if 56 <= program <= 63:  # brass
        return BRASS
    return KEYS
