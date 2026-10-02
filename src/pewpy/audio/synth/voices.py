"""Playing one note of an instrument: its oscillators through its envelope and filter."""

from functools import lru_cache

import numpy as np

from pewpy.audio.synth.filters import filters_of, lowpass_gain
from pewpy.audio.synth.instruments import Instrument, instrument
from pewpy.audio.synth.oscillators import oscillator
from pewpy.audio.synth.signal import RATE, FloatArray, frequency


def envelope(count: int, held: int, attack: float, decay: float, sustain: float, release: float) -> FloatArray:
    """An ADSR envelope over `count` samples, the key held for the first `held` (times in seconds)."""
    t = np.arange(count) / RATE
    rise = np.minimum(t / max(attack, 1e-4), 1.0)
    after = np.maximum(t - attack, 0.0)
    level = rise * (sustain + (1.0 - sustain) * np.exp(-after / max(decay, 1e-4)))
    if held < count:
        at_release = level[held - 1] if held > 0 else 0.0
        level[held:] = at_release * np.exp(-(t[held:] - t[held]) / max(release, 1e-4))
    return level


def voice(spec: Instrument, pitch: int, count: int, held: int) -> FloatArray:
    """One note, stereo (count x 2), before velocity and volume."""
    t = np.arange(count) / RATE
    base = frequency(pitch)
    wobble = 2.0 ** (spec.vibrato / 1200 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(t / 0.3, 1.0))
    out = np.zeros((count, 2))
    for index in range(spec.voices):
        offset = (index / (spec.voices - 1) - 0.5) if spec.voices > 1 else 0.0
        hertz = np.full(count, base * 2.0 ** (offset * spec.detune / 1200)) * wobble
        tone = oscillator(spec.wave, hertz, phase=(index * 0.37) % 1.0)
        pan = np.clip(spec.pan + offset * 2 * spec.spread, -1.0, 1.0)
        out[:, 0] += tone * np.sqrt((1 - pan) / 2)
        out[:, 1] += tone * np.sqrt((1 + pan) / 2)
    out /= np.sqrt(spec.voices)
    if spec.sub:
        sub = oscillator("square", np.full(count, base / 2)) * spec.sub
        out += sub[:, None] * np.sqrt(0.5)
    # The filter's envelope: from bright to its cutoff, as a mix of the two (cheaper than a moving filter).
    bright, dark = filters_of(out, lowpass_gain(spec.cutoff * spec.brightness), lowpass_gain(spec.cutoff))
    opening = np.exp(-t / spec.filter_decay)[:, None]
    shaped = dark + (bright - dark) * opening
    level = envelope(count, held, spec.attack, spec.decay, spec.sustain, spec.release)
    return shaped * level[:, None] * spec.gain


@lru_cache(maxsize=512)
def play_note(program: int, pitch: int, count: int, held: int) -> FloatArray:
    return voice(instrument(program), pitch, count, held)
