import numpy as np
import pytest

from pewpy.audio.synth.instruments import BASS, LEAD, Instrument
from pewpy.audio.synth.signal import RATE
from pewpy.audio.synth.voices import envelope, play_note, voice


def test_the_envelope_rises_holds_and_releases() -> None:
    level = envelope(RATE, RATE // 2, attack=0.01, decay=0.1, sustain=0.5, release=0.05)
    assert level[0] == 0.0
    assert level[int(0.01 * RATE)] == pytest.approx(1.0, abs=0.1)
    assert level[RATE // 2 - 1] == pytest.approx(0.5, abs=0.01)  # held
    assert level[-1] < 0.01  # released


def test_a_key_held_to_the_end_is_never_released() -> None:
    level = envelope(RATE // 10, RATE // 10, attack=0.001, decay=0.01, sustain=0.5, release=0.05)
    assert level[-1] == pytest.approx(0.5, abs=0.01)


def test_a_key_never_held_stays_silent() -> None:
    assert not envelope(100, 0, attack=0.01, decay=0.1, sustain=0.5, release=0.05).any()


def test_a_voice_is_stereo_and_spread_voices_differ_between_sides() -> None:
    sound = voice(LEAD, 69, RATE // 4, RATE // 8)
    assert sound.shape == (RATE // 4, 2)
    assert np.std(sound) > 0
    assert not np.allclose(sound[:, 0], sound[:, 1])


def test_a_single_centered_voice_is_the_same_on_both_sides() -> None:
    sound = voice(Instrument(sub=0.5), 45, RATE // 8, RATE // 16)
    assert np.allclose(sound[:, 0], sound[:, 1])


def test_a_played_note_is_its_programs_instrument_and_kept() -> None:
    note = play_note(38, 40, 1000, 500)
    assert np.allclose(note, voice(BASS, 40, 1000, 500))
    assert play_note(38, 40, 1000, 500) is note
