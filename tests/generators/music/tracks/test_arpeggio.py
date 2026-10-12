from pewpy.generators.music.band import ARP
from pewpy.generators.music.tracks.arpeggio import arp
from tests.generators.music.writing import writer


def test_the_arpeggio_runs_in_sixteenths_through_the_chord() -> None:
    written = writer(arp="up")
    arp(written, 0.0, 2, 0, (0, 3, 7), 70)
    assert len(written.notes) == 32
    assert all(note.channel == ARP for note in written.notes)
    first_bar = [note.pitch % 12 for note in written.notes[:4]]
    assert first_bar == [0, 3, 7, 0]
    assert written.notes[16].pitch == written.notes[0].pitch + 12  # every other bar an octave up
    assert written.notes[0].velocity > written.notes[1].velocity  # accented on the beat
