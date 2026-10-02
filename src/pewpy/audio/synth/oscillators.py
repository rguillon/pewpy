"""Band-limited oscillators, and noise."""

import numpy as np

from pewpy.audio.synth.signal import RATE, FloatArray


def _poly_blep(phase: FloatArray, step: FloatArray) -> FloatArray:
    """Return the correction that removes most of the aliasing from a saw's jump (where phase wraps)."""
    out = np.zeros_like(phase)
    step = np.maximum(step, 1e-9)
    low = phase < step
    t = phase[low] / step[low]
    out[low] = t + t - t * t - 1.0
    high = phase > 1.0 - step
    t = (phase[high] - 1.0) / step[high]
    out[high] = t * t + t + t + 1.0
    return out


def oscillator(wave: str, hertz: FloatArray, phase: float = 0.0) -> FloatArray:
    """`wave` ("saw", "square", "triangle", "sine") following the frequency `hertz` (one per sample)."""
    step = hertz / RATE
    cycle = (np.cumsum(step) - step[0] + phase) % 1.0
    if wave == "sine":
        return np.sin(2 * np.pi * cycle)
    if wave == "triangle":
        return 1.0 - 4.0 * np.abs(cycle - 0.5)
    saw = 2.0 * cycle - 1.0 - _poly_blep(cycle, step)
    if wave == "saw":
        return saw
    shifted = (cycle + 0.5) % 1.0
    return saw - (2.0 * shifted - 1.0 - _poly_blep(shifted, step))  # square: two saws half a cycle apart


def noise(count: int, seed: int = 0) -> FloatArray:
    """Make `count` samples of white noise, the same for the same seed."""
    return np.random.default_rng(seed).uniform(-1.0, 1.0, count)
