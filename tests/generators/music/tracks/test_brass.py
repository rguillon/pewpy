from pewpy.generators.music.band import BRASS
from pewpy.generators.music.tracks.brass import brass
from tests.generators.music.writing import writer


def test_brass_stabs_the_chord_in_two_bar_figures() -> None:
    written = writer()
    brass(written, 0.0, 2, 0, (0, 3, 7))
    assert all(note.channel == BRASS for note in written.notes)
    assert len(written.notes) == (3 + 2) * 3  # three stabs, then two, of three notes each
    assert {note.pitch % 12 for note in written.notes} == {0, 3, 7}
