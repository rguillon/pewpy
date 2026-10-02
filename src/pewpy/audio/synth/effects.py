"""The mix's effects: reverbs, the stereo delay, and ducking under the kick drum."""

import numpy as np

from pewpy.audio.midi import DRUMS, Song
from pewpy.audio.synth.filters import lowpass
from pewpy.audio.synth.oscillators import noise
from pewpy.audio.synth.signal import RATE, FloatArray


def impulse(seconds: float, decay: float, seed: int, gated: bool = False) -> FloatArray:
    """A stereo reverb's impulse response: decaying noise, darker as it fades (or flat then cut, gated)."""
    count = int(seconds * RATE)
    t = np.arange(count) / RATE
    shape = np.where(t < seconds * 0.85, 1.0, np.exp(-(t - seconds * 0.85) / 0.01)) if gated else np.exp(-t / decay)
    sides = [lowpass(noise(count, seed + side), 5000) * shape for side in (0, 1)]
    response = np.stack(sides, axis=1)
    response[: int(0.012 * RATE)] = 0.0  # a short pre-delay
    return response / np.sqrt(np.sum(response**2) / 2)


def convolve(signal: FloatArray, response: FloatArray) -> FloatArray:
    size = len(signal) + len(response)
    fft_size = 1 << (size - 1).bit_length()
    out = np.empty_like(signal)
    for side in (0, 1):
        spectrum = np.fft.rfft(signal[:, side], fft_size) * np.fft.rfft(response[:, side], fft_size)
        out[:, side] = np.fft.irfft(spectrum, fft_size)[: len(signal)]
    return out


def echo(signal: FloatArray, seconds: float, feedback: float = 0.45, repeats: int = 5) -> FloatArray:
    """A ping-pong delay: each repeat on the other side, quieter."""
    out = np.zeros_like(signal)
    step = int(seconds * RATE)
    mono = lowpass(signal.mean(axis=1), 3500)
    for repeat in range(1, repeats + 1):
        if repeat * step >= len(signal):
            break
        out[repeat * step :, repeat % 2] += mono[: len(signal) - repeat * step] * feedback**repeat
    return out


def ducking(song: Song, count: int) -> FloatArray:
    """The volume of whatever ducks under the kick: down at each kick, back up quickly."""
    gain = np.ones(count)
    release = int(0.25 * RATE)
    curve = 1.0 - 0.6 * np.exp(-np.arange(release) / (0.07 * RATE))
    for note in song.notes:
        if note.channel == DRUMS and note.pitch in (35, 36):
            start = int(song.seconds(note.start) * RATE)
            end = min(count, start + release)
            if start < count:
                gain[start:end] = np.minimum(gain[start:end], curve[: end - start])
    return gain
