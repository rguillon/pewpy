"""Picking up an extra life."""

import numpy as np

from pewpy.audio.sfx.shaping import fade
from pewpy.audio.synth import RATE, FloatArray, lowpass, oscillator


def extra_life() -> FloatArray:
    """Make the sound of an extra life: a bright fanfare climbing two octaves, its last note held."""
    parts = []
    for index, semitones in enumerate((0, 4, 7, 12, 16, 19, 24)):
        last = index == 6
        hertz = np.full(int((0.35 if last else 0.07) * RATE), 523.25 * 2 ** (semitones / 12))
        tone = oscillator("square", hertz) + 0.5 * oscillator("triangle", hertz * 2)
        parts.append(fade(tone, 0.25 if last else 0.06, 0.002))
    return lowpass(np.concatenate(parts), 7000) * 0.3
