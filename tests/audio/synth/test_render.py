import io
import wave

import numpy as np

from pewpy.audio.midi import DRUMS, Note, Song
from pewpy.audio.synth.render import place, render, wav_bytes
from pewpy.audio.synth.signal import RATE, TAIL


def song() -> Song:
    notes = [Note(beat, 0.25, 36, 120, DRUMS) for beat in range(4)]
    notes += [Note(0, 4, 45, 100, 0), Note(1, 0.5, 38, 110, DRUMS), Note(2, 1, 81, 100, 1)]
    return Song(tempo=120.0, notes=notes, programs={0: 38, 1: 81}, length=4.0)


def test_a_looping_song_renders_its_exact_length_within_range() -> None:
    samples = render(song())
    assert samples.shape == (2 * RATE, 2)  # 4 beats at 120 bpm, stereo: the tail wraps onto the start
    assert np.max(np.abs(samples)) <= 0.9 + 1e-9
    assert np.std(samples) > 0.05


def test_a_song_played_once_keeps_its_tail() -> None:
    assert len(render(song(), loop=False)) == int((2.0 + TAIL) * RATE)


def test_toms_ring_in_the_reverb() -> None:
    toms = Song(tempo=120.0, notes=[Note(0.0, 0.25, 45, 120, DRUMS)], length=1.0)
    assert np.std(render(toms)) > 0


def test_a_sound_is_added_from_its_start_and_cut_at_the_end() -> None:
    target = np.ones((10, 2))
    place(target, np.ones((5, 2)), 7)
    assert target[:7].tolist() == [[1.0, 1.0]] * 7
    assert target[7:].tolist() == [[2.0, 2.0]] * 3


def test_what_starts_past_the_end_is_left_out() -> None:
    target = np.zeros((10, 2))
    place(target, np.ones((5, 2)), 10)
    assert not target.any()


def test_wav_bytes_are_a_wav_file() -> None:
    data = wav_bytes(np.zeros((100, 2)))
    with wave.open(io.BytesIO(data)) as read:
        assert (read.getnchannels(), read.getframerate(), read.getnframes()) == (2, RATE, 100)


def test_mono_samples_make_a_mono_wav_file_at_any_rate() -> None:
    data = wav_bytes(np.zeros(50), rate=8000)
    with wave.open(io.BytesIO(data)) as read:
        assert (read.getnchannels(), read.getframerate(), read.getnframes()) == (1, 8000, 50)
