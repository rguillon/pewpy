import pytest

from pewpy.audio import midi
from pewpy.audio.midi import DRUMS, MidiError, Note, Song


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


def test_a_song_written_then_read_is_the_same() -> None:
    song = make_song()
    back = midi.read(midi.write(song, "a song"))
    assert back.tempo == pytest.approx(100.0, rel=1e-4)
    assert back.notes == sorted(song.notes, key=lambda note: (note.start, note.channel, note.pitch))
    assert back.programs == song.programs
    assert back.volumes == song.volumes
    assert back.length == 8.0  # the loop marker


def test_a_note_ending_where_the_same_one_starts_stays_two_notes() -> None:
    song = Song(tempo=120.0, notes=[Note(0.0, 1.0, 60), Note(1.0, 1.0, 60)])
    assert midi.read(midi.write(song)).notes == song.notes


def test_tempo_changes_move_later_beats() -> None:
    song = Song(tempo=120.0, notes=[Note(0.0, 8.0, 60)], tempo_changes=[(4.0, 60.0)])
    assert song.seconds(4.0) == pytest.approx(2.0)  # 4 beats at 120 bpm
    assert song.seconds(6.0) == pytest.approx(4.0)  # then 2 at 60
    back = midi.read(midi.write(song))
    assert back.tempo_changes == [(4.0, pytest.approx(60.0))]
    assert back.duration == pytest.approx(6.0)


def test_running_status_and_note_on_with_no_velocity_are_read() -> None:
    # One track: note on 60, then (running status) note on 60 at velocity 0 = off, a beat later.
    events = bytes([0x00, 0x90, 60, 100, 0x83, 0x60, 60, 0, 0x00, 0xFF, 0x2F, 0x00])
    data = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 0, 0, 1, 0x01, 0xE0])
    data += b"MTrk" + len(events).to_bytes(4, "big") + events
    song = midi.read(data)
    assert song.notes == [Note(0.0, 1.0, 60, 100, 0)]
    assert song.tempo == 120.0  # none given


@pytest.mark.parametrize("data", [b"RIFF0000", b"MThd\x00\x00\x00\x06\x00\x01\x00\x02"])
def test_what_isnt_midi_is_refused(data: bytes) -> None:
    with pytest.raises(MidiError):
        midi.read(data)


def midi_file(*tracks: tuple[bytes, bytes], per_beat: int = 480) -> bytes:
    data = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 1]) + len(tracks).to_bytes(2, "big")
    data += per_beat.to_bytes(2, "big")
    for kind, events in tracks:
        data += kind + len(events).to_bytes(4, "big") + events
    return data


def test_what_the_game_doesnt_use_is_skipped() -> None:
    events = bytes([
        0x00,
        0xD0,
        40,  # channel pressure: one data byte
        0x00,
        0xB0,
        10,
        64,  # a controller other than the volume (pan)
        0x00,
        0xF0,
        0x02,
        0x01,
        0x02,  # system exclusive
        0x00,
        0x90,
        60,
        100,
        0x83,
        0x60,
        0x80,
        60,
        0,
    ])  # and no end of track: the track's end is enough
    song = midi.read(midi_file((b"XTRA", b"\x01\x02\x03"), (b"MTrk", events)))
    assert song.notes == [Note(0.0, 1.0, 60, 100, 0)]
    assert song.programs == {}
    assert song.volumes == {}


def test_smpte_timing_is_refused() -> None:
    with pytest.raises(MidiError, match="SMPTE"):
        midi.read(midi_file(per_beat=0xE728))
