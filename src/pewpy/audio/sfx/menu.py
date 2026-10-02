"""The menus: moving, choosing, going back."""

import numpy as np

from pewpy.audio.sfx.shaping import fade
from pewpy.audio.synth import RATE, FloatArray, lowpass, oscillator


def menu_move() -> FloatArray:
    return fade(lowpass(oscillator("square", np.full(int(0.045 * RATE), 880.0)), 4000), 0.02, 0.001) * 0.2


def menu_choose() -> FloatArray:
    low = fade(oscillator("square", np.full(int(0.06 * RATE), 660.0)), 0.05, 0.001)
    high = fade(oscillator("square", np.full(int(0.12 * RATE), 1320.0)), 0.07, 0.001)
    return lowpass(np.concatenate([low, high]), 5000) * 0.25


def menu_back() -> FloatArray:
    high = fade(oscillator("square", np.full(int(0.06 * RATE), 880.0)), 0.05, 0.001)
    low = fade(oscillator("square", np.full(int(0.1 * RATE), 440.0)), 0.06, 0.001)
    return lowpass(np.concatenate([high, low]), 4000) * 0.25
