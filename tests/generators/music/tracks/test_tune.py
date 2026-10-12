from pewpy.generators.music.band import LEAD
from pewpy.generators.music.tracks.tune import make_motif, tune, tune_pitch
from tests.generators.music.writing import writer


def test_a_motif_is_two_bars_the_second_ending_long() -> None:
    motif = make_motif(writer())
    assert all(0 <= start < 8 for start, _ in motif)
    last_start, last_length = motif[-1]
    assert last_start + last_length == 8
    assert last_length >= 2.5


def test_on_the_beat_the_tune_plays_a_chord_note_in_the_lead_range() -> None:
    written = writer(key="C")
    written.last_tune = 72
    for _ in range(20):
        pitch = tune_pitch(written, {0, 3, 7}, on_beat=True)
        assert pitch % 12 in {0, 3, 7}
        assert 67 <= pitch <= 86
    step = tune_pitch(written, {0, 3, 7}, on_beat=False)
    assert abs(step - 72) <= 4


def test_the_tune_ends_on_the_tonic() -> None:
    written = writer(key="E")
    written.last_tune = 76
    tune(written, 0.0, [written.chord("i"), written.chord("VI")], 2)
    assert all(note.channel == LEAD for note in written.notes)
    assert written.notes[-1].pitch % 12 == written.tonic
