import numpy as np
import pytest

from pewpy.audio.midi import DRUMS, Note, Song
from pewpy.audio.synth.effects import convolve, ducking, echo, impulse
from pewpy.audio.synth.signal import RATE


def test_the_echo_stops_at_the_end_of_the_sound() -> None:
    short = np.ones((100, 2))
    echoed = echo(short, seconds=50 / RATE, repeats=5)  # only the first repeat fits
    assert np.count_nonzero(echoed[:, 1]) > 0
    assert np.count_nonzero(echoed[:50]) == 0


def test_an_impulse_is_stereo_waits_a_moment_and_has_unit_power() -> None:
    response = impulse(0.5, 0.2, 1)
    assert response.shape == (RATE // 2, 2)
    assert not response[: int(0.012 * RATE)].any()  # the pre-delay
    assert np.sum(response**2) / 2 == pytest.approx(1.0)


def test_a_gated_impulse_is_cut_short() -> None:
    gated = impulse(0.3, 1.0, 1, gated=True)
    held, cut = gated[len(gated) // 3 : len(gated) * 2 // 3], gated[-100:]
    assert np.std(cut) < 0.1 * np.std(held)
    long = impulse(0.3, 1.0, 1)
    assert np.std(long[-100:]) > 0.5 * np.std(long[len(long) // 3 : len(long) * 2 // 3])


def test_convolving_with_a_single_click_delays_the_signal() -> None:
    signal = np.zeros((50, 2))
    signal[0] = [1.0, 0.5]
    click = np.zeros((10, 2))
    click[3] = 1.0
    out = convolve(signal, click)
    assert out.shape == signal.shape
    assert out[3] == pytest.approx([1.0, 0.5])


def test_whatever_ducks_goes_down_at_each_kick_then_back_up() -> None:
    song = Song(tempo=120.0, notes=[Note(1.0, 0.25, 36, 120, DRUMS), Note(0.0, 0.25, 38, 120, DRUMS)])
    gain = ducking(song, RATE * 2)
    assert gain[0] == 1.0  # a snare doesn't duck
    assert gain[RATE // 2] == pytest.approx(0.4)  # the kick, a beat in
    assert gain[RATE] == 1.0


def test_a_kick_past_the_end_ducks_nothing() -> None:
    late_kick = Song(tempo=120.0, notes=[Note(100.0, 0.25, 36, 120, DRUMS)])
    assert ducking(late_kick, 1000).min() == 1.0
