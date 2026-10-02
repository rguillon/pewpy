"""What the sound effects are made of: time, glides, fades, booms."""

import numpy as np

from pewpy.audio.synth import RATE, FloatArray, lowpass, noise, oscillator


def span(seconds: float) -> FloatArray:
    """Return the times of `seconds` of samples."""
    return np.arange(int(seconds * RATE)) / RATE


def glide(seconds: float, start: float, end: float, curve: float = 1.0) -> FloatArray:
    """Make a frequency going from `start` to `end` (exponentially, faster at first when `curve` > 1)."""
    progress = (span(seconds) / seconds) ** (1 / curve)
    return start * (end / start) ** progress


def fade(signal: FloatArray, decay: float, attack: float = 0.002) -> FloatArray:
    """Shape a signal with a quick attack and an exponential decay."""
    t = np.arange(len(signal)) / RATE
    return signal * np.minimum(t / attack, 1.0) * np.exp(-t / decay)


def boom(seconds: float, cutoff: float, thump: float, seed: int) -> FloatArray:
    """Make an explosion: noise whose filter closes as it fades, over a low thump."""
    t = span(seconds)
    rumble = noise(len(t), seed)
    bright = lowpass(rumble, cutoff)
    dark = lowpass(rumble, cutoff / 6)
    closing = np.exp(-t / (seconds / 5))
    body = (dark + (bright - dark) * closing) * np.exp(-t / (seconds / 3.5))
    low = oscillator("sine", glide(seconds, thump, thump / 2.5, 3.0)) * np.exp(-t / (seconds / 4))
    return np.tanh(2.2 * body + 0.9 * low) * 0.8
