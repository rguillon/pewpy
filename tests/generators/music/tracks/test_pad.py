from pewpy.generators.music.band import PAD
from pewpy.generators.music.tracks.pad import pad
from tests.generators.music.writing import writer


def test_the_pad_holds_the_voiced_chord_its_bars_long() -> None:
    written = writer()
    pad(written, 4.0, 2, 0, (0, 3, 7), 60)
    assert len(written.notes) == 3
    assert all(note.channel == PAD and note.start == 4.0 and note.length == 8 - 0.05 for note in written.notes)
    assert tuple(note.pitch for note in written.notes) == written.voicing
