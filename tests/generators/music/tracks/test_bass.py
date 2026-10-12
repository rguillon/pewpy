import pytest

from pewpy.generators.music.band import BASS
from pewpy.generators.music.tracks.bass import bass
from tests.generators.music.writing import writer


@pytest.mark.parametrize(("style", "per_bar"), [("eighths", 8), ("gallop", 12), ("sixteenths", 16)])
def test_the_bass_plays_the_root_in_its_style(style: str, per_bar: int) -> None:
    written = writer(bass=style)
    bass(written, 0.0, 2, 5)
    assert len(written.notes) == 2 * per_bar
    assert all(note.channel == BASS for note in written.notes)
    assert {note.pitch % 12 for note in written.notes} == {5}
    assert all(note.pitch < 60 for note in written.notes)
