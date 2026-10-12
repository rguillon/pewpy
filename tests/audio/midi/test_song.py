import pytest

from pewpy.audio.midi.song import MidiError, Note, Song


def test_tempo_changes_move_later_beats() -> None:
    song = Song(tempo=120.0, notes=[Note(0.0, 8.0, 60)], tempo_changes=[(4.0, 60.0)])
    assert song.seconds(4.0) == pytest.approx(2.0)  # 4 beats at 120 bpm
    assert song.seconds(6.0) == pytest.approx(4.0)  # then 2 at 60
    assert song.duration == pytest.approx(6.0)


def test_a_song_loops_at_its_length_or_else_at_the_end_of_its_last_note() -> None:
    notes = [Note(0.0, 1.0, 60), Note(2.0, 1.5, 62)]
    assert Song(tempo=120.0, notes=notes).beats == 3.5
    assert Song(tempo=120.0, notes=notes, length=8.0).beats == 8.0
    assert Song(tempo=120.0).beats == 0.0


def test_a_note_is_middle_loud_on_the_first_channel_unless_told() -> None:
    note = Note(0.0, 1.0, 60)
    assert (note.velocity, note.channel) == (100, 0)


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (MidiError.not_midi(), "not a standard MIDI file"),
        (MidiError.truncated(), "ends too soon"),
        (MidiError.smpte(), "SMPTE"),
    ],
)
def test_each_midi_error_says_what_went_wrong(error: MidiError, message: str) -> None:
    assert isinstance(error, ValueError)
    assert message in str(error)
