"""A shot hitting."""

import numpy as np

from pewpy.audio.sfx.shaping import fade, span
from pewpy.audio.synth import FloatArray, highpass, noise, oscillator


def hit() -> FloatArray:
    """Make the sound of an enemy hit: a short metallic tick."""
    t = span(0.07)
    tick = highpass(noise(len(t), 8), 2500) + 0.6 * oscillator("triangle", np.full(len(t), 1100.0))
    return fade(tick, 0.015) * 0.3
