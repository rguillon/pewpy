"""The drums (channel 9): each one synthesized from noise and sweeps."""

from functools import cache

import numpy as np

from pewpy.audio.synth.filters import highpass, lowpass
from pewpy.audio.synth.oscillators import noise, oscillator
from pewpy.audio.synth.signal import RATE, FloatArray


def _sweep(count: int, start: float, end: float, speed: float) -> FloatArray:
    t = np.arange(count) / RATE
    return end + (start - end) * np.exp(-t * speed)


@cache
def drum(pitch: int) -> FloatArray:
    """A General MIDI drum (mono): kicks, snares and claps, hats, crashes, toms; anything else is a click."""
    if pitch in (35, 36):  # kick
        count = int(0.45 * RATE)
        body = oscillator("sine", _sweep(count, 160, 45, 30)) * np.exp(-np.arange(count) / (0.28 * RATE))
        click = lowpass(noise(count, 1), 3000) * np.exp(-np.arange(count) / (0.004 * RATE))
        return np.tanh(1.6 * body + 0.4 * click) * 0.9
    if pitch in (38, 39, 40):  # snare, clap
        count = int(0.35 * RATE)
        decay = np.exp(-np.arange(count) / (0.09 * RATE))
        rattle = highpass(lowpass(noise(count, 2), 7000), 900) * decay
        tone = oscillator("triangle", _sweep(count, 260, 180, 20)) * np.exp(-np.arange(count) / (0.05 * RATE))
        return (0.75 * rattle + 0.45 * tone) * (0.8 if pitch == 39 else 1.0)
    if pitch in (42, 44, 46):  # hats: closed, pedal, open
        length = 0.4 if pitch == 46 else 0.06
        count = int(length * RATE * 1.5)
        return highpass(noise(count, 3), 7000) * np.exp(-np.arange(count) / (length / 3 * RATE)) * 0.35
    if pitch in (49, 51, 52, 55, 57, 59):  # cymbals
        count = int(2.5 * RATE)
        return highpass(noise(count, 4), 4000) * np.exp(-np.arange(count) / (0.7 * RATE)) * 0.25
    if 41 <= pitch <= 50:  # toms, low to high
        count = int(0.6 * RATE)
        top = 90 + (pitch - 41) * 18
        body = oscillator("sine", _sweep(count, top * 1.6, top, 12)) * np.exp(-np.arange(count) / (0.22 * RATE))
        return body * 0.7
    count = int(0.03 * RATE)
    return highpass(noise(count, 5), 2000) * np.exp(-np.arange(count) / (0.005 * RATE)) * 0.3


DRUM_PANS = {42: 0.3, 44: 0.3, 46: 0.3, 41: -0.4, 43: -0.25, 45: -0.1, 47: 0.1, 48: 0.25, 50: 0.4, 49: -0.3, 57: 0.3}
