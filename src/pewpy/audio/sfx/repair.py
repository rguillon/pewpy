"""Picking up a repair."""

import numpy as np

from pewpy.audio.sfx.shaping import glide, span
from pewpy.audio.synth import FloatArray, oscillator


def repair() -> FloatArray:
    """Repaired: a bright glide up with a sparkle."""
    t = span(0.4)
    rising = oscillator("triangle", glide(0.4, 400, 1600)) * np.sin(np.pi * t / 0.4)
    sparkle = oscillator("sine", np.full(len(t), 2637.0)) * (np.sin(2 * np.pi * 20 * t) > 0) * t / 0.4 * 0.3
    return (rising + sparkle) * 0.4
