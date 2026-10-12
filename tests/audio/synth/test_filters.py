import numpy as np
import pytest

from pewpy.audio.synth.filters import filters_of, highpass, lowpass, lowpass_gain
from pewpy.audio.synth.oscillators import oscillator
from pewpy.audio.synth.signal import RATE


def test_the_low_pass_keeps_lows_and_cuts_highs() -> None:
    low = oscillator("sine", np.full(RATE, 200.0))
    high = oscillator("sine", np.full(RATE, 8000.0))
    assert np.std(lowpass(low, 1000)) == pytest.approx(np.std(low), rel=0.05)
    assert np.std(lowpass(high, 1000)) < 0.05 * np.std(high)
    assert np.std(highpass(low, 4000)) < 0.05 * np.std(low)


def test_a_low_pass_above_what_can_be_heard_changes_nothing() -> None:
    signal = oscillator("saw", np.full(1000, 440.0))
    assert lowpass(signal, RATE) is signal


def test_the_low_pass_gain_is_whole_below_its_cutoff_and_halved_in_power_at_it() -> None:
    gain = lowpass_gain(1000.0)(np.array([0.0, 1000.0, 10_000.0]))
    assert gain[0] == pytest.approx(1.0)
    assert gain[1] == pytest.approx(1 / np.sqrt(2))
    assert gain[2] < 0.02


def test_stereo_signals_are_filtered_side_by_side_through_every_filter_at_once() -> None:
    left = oscillator("sine", np.full(RATE // 4, 200.0))
    stereo = np.stack([left, -left], axis=1)
    keep, cut = filters_of(stereo, np.ones_like, np.zeros_like)
    assert keep.shape == cut.shape == stereo.shape
    assert np.allclose(keep, stereo)
    assert np.allclose(cut, 0.0)
