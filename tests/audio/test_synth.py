import io
import wave

import numpy as np
import pytest

from pewpy.audio import synth
from pewpy.audio.midi import DRUMS, Note, Song
from pewpy.audio.synth import RATE


def loudest_frequency(signal: np.ndarray) -> float:
    spectrum = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))
    return float(np.fft.rfftfreq(len(signal), 1 / RATE)[np.argmax(spectrum)])


@pytest.mark.parametrize("wave_name", ["saw", "square", "triangle", "sine"])
def test_oscillators_play_their_frequency(wave_name):
    tone = synth.oscillator(wave_name, np.full(RATE // 2, 440.0))
    assert loudest_frequency(tone) == pytest.approx(440.0, abs=3)
    assert np.max(np.abs(tone)) <= 1.2


def test_the_low_pass_keeps_lows_and_cuts_highs():
    low = synth.oscillator("sine", np.full(RATE, 200.0))
    high = synth.oscillator("sine", np.full(RATE, 8000.0))
    assert np.std(synth.lowpass(low, 1000)) == pytest.approx(np.std(low), rel=0.05)
    assert np.std(synth.lowpass(high, 1000)) < 0.05 * np.std(high)
    assert np.std(synth.highpass(low, 4000)) < 0.05 * np.std(low)


def test_the_envelope_rises_holds_and_releases():
    level = synth.envelope(RATE, RATE // 2, attack=0.01, decay=0.1, sustain=0.5, release=0.05)
    assert level[0] == 0.0
    assert level[int(0.01 * RATE)] == pytest.approx(1.0, abs=0.1)
    assert level[RATE // 2 - 1] == pytest.approx(0.5, abs=0.01)  # held
    assert level[-1] < 0.01  # released


@pytest.mark.parametrize(
    ("program", "expected"),
    [(38, synth.BASS), (89, synth.PAD), (80, synth.PLUCK), (81, synth.LEAD), (61, synth.BRASS), (0, synth.KEYS)],
)
def test_each_general_midi_family_has_an_instrument(program, expected):
    assert synth.instrument(program) is expected


def song() -> Song:
    notes = [Note(beat, 0.25, 36, 120, DRUMS) for beat in range(4)]
    notes += [Note(0, 4, 45, 100, 0), Note(1, 0.5, 38, 110, DRUMS), Note(2, 1, 81, 100, 1)]
    return Song(tempo=120.0, notes=notes, programs={0: 38, 1: 81}, length=4.0)


def test_a_looping_song_renders_its_exact_length_within_range():
    samples = synth.render(song())
    assert samples.shape == (2 * RATE, 2)  # 4 beats at 120 bpm, stereo: the tail wraps onto the start
    assert np.max(np.abs(samples)) <= 0.9 + 1e-9
    assert np.std(samples) > 0.05


def test_a_song_played_once_keeps_its_tail():
    assert len(synth.render(song(), loop=False)) == int((2.0 + synth.TAIL) * RATE)


def test_every_drum_sounds():
    for pitch in (36, 38, 39, 42, 46, 49, 41, 45, 50, 80):
        hit = synth.drum(pitch)
        assert len(hit) > 0
        assert 0 < np.max(np.abs(hit)) <= 1.0


def test_wav_bytes_are_a_wav_file():
    data = synth.wav_bytes(np.zeros((100, 2)))
    with wave.open(io.BytesIO(data)) as read:
        assert (read.getnchannels(), read.getframerate(), read.getnframes()) == (2, RATE, 100)


def test_a_low_pass_above_what_can_be_heard_changes_nothing():
    signal = synth.oscillator("saw", np.full(1000, 440.0))
    assert synth.lowpass(signal, RATE) is signal


def test_a_key_held_to_the_end_is_never_released():
    level = synth.envelope(RATE // 10, RATE // 10, attack=0.001, decay=0.01, sustain=0.5, release=0.05)
    assert level[-1] == pytest.approx(0.5, abs=0.01)


def test_the_echo_stops_at_the_end_of_the_sound():
    short = np.ones((100, 2))
    echoed = synth._echo(short, seconds=50 / RATE, repeats=5)  # only the first repeat fits
    assert np.count_nonzero(echoed[:, 1]) > 0 and np.count_nonzero(echoed[:50]) == 0


def test_what_starts_past_the_end_is_left_out():
    target = np.zeros((10, 2))
    synth._place(target, np.ones((5, 2)), 10)
    assert not target.any()
    late_kick = Song(tempo=120.0, notes=[Note(100.0, 0.25, 36, 120, DRUMS)])
    assert synth._ducking(late_kick, 1000).min() == 1.0


def test_toms_ring_in_the_reverb():
    toms = Song(tempo=120.0, notes=[Note(0.0, 0.25, 45, 120, DRUMS)], length=1.0)
    assert np.std(synth.render(toms)) > 0
