"""Switching weapons."""

import numpy as np

from pewpy.audio.sfx.shaping import fade
from pewpy.audio.synth import RATE, FloatArray, lowpass, oscillator


def switch() -> FloatArray:
    """Make the sound of the weapon switched: two quick blips."""
    first = fade(oscillator("square", np.full(int(0.04 * RATE), 660.0)), 0.03, 0.001)
    second = fade(oscillator("square", np.full(int(0.05 * RATE), 990.0)), 0.035, 0.001)
    return lowpass(np.concatenate([first, np.zeros(int(0.015 * RATE)), second]), 5000) * 0.25
