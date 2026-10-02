"""Picking up an upgrade or a secondary weapon."""

import numpy as np

from pewpy.audio.sfx.shaping import fade
from pewpy.audio.synth import RATE, FloatArray, lowpass, oscillator


def pickup() -> FloatArray:
    """A weapon upgrade: a major arpeggio up."""
    parts = []
    for semitones in (0, 4, 7, 12):
        hertz = np.full(int(0.06 * RATE), 1046.5 * 2 ** (semitones / 12))
        parts.append(fade(oscillator("square", hertz), 0.05, 0.001))
    return lowpass(np.concatenate(parts), 6000) * 0.3
