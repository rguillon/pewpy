"""The laser's hum."""

import numpy as np

from pewpy.audio.sfx.shaping import span
from pewpy.audio.synth import RATE, FloatArray, oscillator


def laser() -> FloatArray:
    """The laser's hum, looping (1 s: every frequency a whole number of hertz)."""
    t = span(1.0)
    hum = oscillator("saw", np.full(len(t), 110.0)) + 0.7 * oscillator("saw", np.full(len(t), 221.0))
    shimmer = 0.25 * oscillator("square", np.full(len(t), 662.0))
    wobble = 0.75 + 0.25 * np.sin(2 * np.pi * 12 * t)
    signal = (hum + shimmer) * wobble
    size = len(signal)  # filtered as one cycle of a repeating signal, so the ends meet
    spectrum = np.fft.rfft(signal)
    spectrum /= np.sqrt(1.0 + (np.fft.rfftfreq(size, 1.0 / RATE) / 1800) ** 4)
    return np.fft.irfft(spectrum, size) * 0.16
