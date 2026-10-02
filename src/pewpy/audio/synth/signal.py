"""Samples and pitches."""

import numpy as np

RATE = 32_000  # samples per second
TAIL = 3.0  # seconds rendered past the end, for the release and reverb (wrapped to the start when looping)
FloatArray = np.ndarray


def frequency(pitch: float) -> float:
    """Return a MIDI pitch's frequency, in hertz."""
    return 440.0 * 2.0 ** ((pitch - 69) / 12)
