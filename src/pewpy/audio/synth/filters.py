"""Low-pass and high-pass filters (in the frequency domain)."""

from collections.abc import Callable

import numpy as np

from pewpy.audio.synth.signal import RATE, FloatArray


def filters_of(signal: FloatArray, *responses: Callable[[FloatArray], FloatArray]) -> list[FloatArray]:
    """Pass `signal` (mono, or stereo in columns) through each filter, given by its gain at every frequency.

    In the frequency domain, transformed once for them all (padded to a power of two: much faster, and nothing wraps
    around from the end to the start).
    """
    size = 1 << (len(signal) - 1).bit_length()
    hertz = np.fft.rfftfreq(size, 1.0 / RATE)
    spectrum = np.fft.rfft(signal, size, axis=0)
    gains = [response(hertz) for response in responses]
    shaped = [spectrum * (gain[:, None] if signal.ndim == 2 else gain) for gain in gains]
    return [np.fft.irfft(each, size, axis=0)[: len(signal)] for each in shaped]


def _filter(signal: FloatArray, response: Callable[[FloatArray], FloatArray]) -> FloatArray:
    return filters_of(signal, response)[0]


def lowpass_gain(cutoff: float, order: int = 2) -> Callable[[FloatArray], FloatArray]:
    """Return a Butterworth-shaped low-pass's gain at every frequency."""
    return lambda hertz: 1.0 / np.sqrt(1.0 + (hertz / max(cutoff, 1.0)) ** (2 * order))


def lowpass(signal: FloatArray, cutoff: float, order: int = 2) -> FloatArray:
    """Low-pass `signal`, Butterworth-shaped (12 dB per octave at order 2)."""
    if cutoff >= RATE / 2:
        return signal
    return _filter(signal, lowpass_gain(cutoff, order))


def highpass(signal: FloatArray, cutoff: float, order: int = 2) -> FloatArray:
    """High-pass `signal`, Butterworth-shaped."""
    return _filter(signal, lambda hertz: 1.0 / np.sqrt(1.0 + (cutoff / np.maximum(hertz, 1e-3)) ** (2 * order)))
