from pewpy.generators.music.harmony import CHORDS, MINOR
from pewpy.generators.music.writer import near, voice
from tests.generators.music.writing import writer


def test_a_notes_velocity_stays_within_midis_range() -> None:
    written = writer()
    written.add(0, 0.0, 1.0, 60, 200)
    written.add(0, 1.0, 1.0, 60, -5)
    assert [note.velocity for note in written.notes] == [127, 1]


def test_a_chord_is_named_in_the_songs_key() -> None:
    written = writer(key="A")
    assert written.chord("VI") == ((9 + CHORDS["VI"][0]) % 12, CHORDS["VI"][1])


def test_the_scale_is_the_keys_minor_scale_over_four_octaves() -> None:
    written = writer(key="C")
    scale = written.scale()
    assert all((pitch - written.tonic) % 12 in MINOR for pitch in scale)
    assert scale[-1] - scale[0] >= 36


def test_the_nearest_note_of_a_pitch_class() -> None:
    assert near(0, 62) == 60
    assert near(0, 67) == 72
    assert near(7, 60) == 55


def test_chords_are_voiced_moving_as_little_as_possible() -> None:
    written = writer()
    first = voice(written, 0, (0, 3, 7))
    assert sorted(note % 12 for note in first) == [0, 3, 7]
    written.voicing = first
    second = voice(written, 5, (0, 3, 7))
    assert sorted(note % 12 for note in second) == [0, 5, 8]
    assert abs(sum(second) / 3 - sum(first) / 3) <= 5
