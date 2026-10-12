import numpy as np
import pytest

from pewpy.audio.synth.oscillators import noise, oscillator
from pewpy.audio.synth.signal import RATE


def loudest_frequency(signal: np.ndarray) -> float:
    spectrum = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))
    return float(np.fft.rfftfreq(len(signal), 1 / RATE)[np.argmax(spectrum)])


@pytest.mark.parametrize("wave_name", ["saw", "square", "triangle", "sine"])
def test_oscillators_play_their_frequency(wave_name: str) -> None:
    tone = oscillator(wave_name, np.full(RATE // 2, 440.0))
    assert loudest_frequency(tone) == pytest.approx(440.0, abs=3)
    assert np.max(np.abs(tone)) <= 1.2


def test_a_phase_starts_the_wave_further_along() -> None:
    hertz = np.full(100, 440.0)
    assert oscillator("sine", hertz)[0] == pytest.approx(0.0)
    assert oscillator("sine", hertz, phase=0.25)[0] == pytest.approx(1.0)


def test_noise_is_the_same_for_the_same_seed_and_in_range() -> None:
    first = noise(1000, 3)
    assert np.array_equal(first, noise(1000, 3))
    assert not np.array_equal(first, noise(1000, 4))
    assert np.max(np.abs(first)) <= 1.0
