import pytest

from pewpy.audio.midi.reader import read
from pewpy.audio.midi.song import DRUMS, TICKS_PER_BEAT, Note, Song
from pewpy.audio.midi.writer import write


def make_song() -> Song:
    return Song(
        tempo=100.0,
        notes=[
            Note(0.0, 1.0, 60, 100, 0),
            Note(0.0, 4.0, 48, 90, 1),
            Note(1.0, 0.5, 64, 80, 0),
            Note(1.0, 0.25, 36, 120, DRUMS),
        ],
        programs={0: 81, 1: 38},
        volumes={0: 110},
        length=8.0,
    )


def test_a_song_is_written_as_a_format_1_file_with_a_track_per_channel() -> None:
    data = write(make_song())
    assert data[:4] == b"MThd"
    assert int.from_bytes(data[8:10], "big") == 1  # format 1
    assert int.from_bytes(data[10:12], "big") == 4  # the tempo track, then channels 0, 1 and the drums
    assert int.from_bytes(data[12:14], "big") == TICKS_PER_BEAT
    assert data.count(b"MTrk") == 4


def test_a_song_written_then_read_is_the_same() -> None:
    song = make_song()
    back = read(write(song, "a song"))
    assert back.tempo == pytest.approx(100.0, rel=1e-4)
    assert back.notes == sorted(song.notes, key=lambda note: (note.start, note.channel, note.pitch))
    assert back.programs == song.programs
    assert back.volumes == song.volumes
    assert back.length == 8.0  # the loop marker
    assert back.title == "a song"


def test_a_note_ending_where_the_same_one_starts_stays_two_notes() -> None:
    song = Song(tempo=120.0, notes=[Note(0.0, 1.0, 60), Note(1.0, 1.0, 60)])
    assert read(write(song)).notes == song.notes


def test_tempo_changes_are_written() -> None:
    song = Song(tempo=120.0, notes=[Note(0.0, 8.0, 60)], tempo_changes=[(4.0, 60.0)])
    back = read(write(song))
    assert back.tempo_changes == [(4.0, pytest.approx(60.0))]
    assert back.duration == pytest.approx(6.0)
