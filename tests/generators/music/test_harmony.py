from pewpy.generators.music.harmony import ARPS, CHORDS, MINOR, NOTES, RHYTHMS


def test_the_chords_roots_are_of_the_minor_key_but_its_borrowed_ones() -> None:
    borrowed = {"bII", "V", "I"}  # a Neapolitan, a major dominant, a Picardy third
    for name, (root, shape) in CHORDS.items():
        assert shape[0] == 0
        assert len(shape) in (3, 4)
        if name not in borrowed:
            assert root in MINOR


def test_every_note_name_is_a_pitch_class() -> None:
    assert sorted(NOTES.values()) == list(range(12))


def test_every_rhythm_fills_one_bar_in_order() -> None:
    for rhythm in RHYTHMS:
        starts = [start for start, _ in rhythm]
        assert starts == sorted(starts)
        assert all(start + length <= 4 for start, length in rhythm)


def test_every_arpeggio_plays_the_four_notes_it_has() -> None:
    assert all(set(pattern) <= {0, 1, 2, 3} for pattern in ARPS.values())
