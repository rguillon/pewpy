"""A missile launched."""

import numpy as np

from pewpy.audio.sfx.shaping import glide, span
from pewpy.audio.synth import FloatArray, lowpass, noise, oscillator


def missile() -> FloatArray:
    """A missile launched: a rising whoosh."""
    t = span(0.35)
    whoosh = lowpass(noise(len(t), 7), 2500) * np.sin(np.pi * t / 0.35) ** 2
    tone = oscillator("saw", glide(0.35, 140, 420)) * 0.25
    return lowpass(whoosh + tone, 3000) * 0.5
