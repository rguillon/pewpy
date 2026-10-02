"""A boss coming."""

import numpy as np

from pewpy.audio.sfx.shaping import fade, span
from pewpy.audio.synth import FloatArray, lowpass, oscillator


def alarm() -> FloatArray:
    """Make the sound of a boss coming: a two-tone siren, three times."""
    t = span(1.5)
    hertz = np.where((t * 4).astype(int) % 2 == 0, 620.0, 465.0)
    siren = oscillator("saw", hertz) * (0.6 + 0.4 * np.sin(np.pi * (t * 4 % 1)))
    return fade(lowpass(siren, 2200), 1.2, 0.01) * 0.3
