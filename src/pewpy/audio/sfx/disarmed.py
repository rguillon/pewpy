"""The secondary weapon lost."""

import numpy as np

from pewpy.audio.sfx.shaping import boom, fade, glide
from pewpy.audio.synth import FloatArray, lowpass, oscillator


def disarmed() -> FloatArray:
    """A hit took the secondary weapon: a short crunch and a falling blip."""
    blip = fade(oscillator("square", glide(0.3, 900, 220)), 0.1)
    return np.tanh(boom(0.3, 4000, 160, 23) + lowpass(blip, 4000) * 0.6) * 0.5
