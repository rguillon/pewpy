import pytest

from pewpy.audio.midi.reader import read
from pewpy.audio.midi.song import MidiError, Note


def midi_file(*tracks: tuple[bytes, bytes], per_beat: int = 480) -> bytes:
    data = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 1]) + len(tracks).to_bytes(2, "big")
    data += per_beat.to_bytes(2, "big")
    for kind, events in tracks:
        data += kind + len(events).to_bytes(4, "big") + events
    return data


def test_running_status_and_note_on_with_no_velocity_are_read() -> None:
    # One track: note on 60, then (running status) note on 60 at velocity 0 = off, a beat later.
    events = bytes([0x00, 0x90, 60, 100, 0x83, 0x60, 60, 0, 0x00, 0xFF, 0x2F, 0x00])
    data = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 0, 0, 1, 0x01, 0xE0])
    data += b"MTrk" + len(events).to_bytes(4, "big") + events
    song = read(data)
    assert song.notes == [Note(0.0, 1.0, 60, 100, 0)]
    assert song.tempo == 120.0  # none given


@pytest.mark.parametrize("data", [b"RIFF0000", b"MThd\x00\x00\x00\x06\x00\x01\x00\x02"])
def test_what_isnt_midi_is_refused(data: bytes) -> None:
    with pytest.raises(MidiError):
        read(data)


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
    song = read(midi_file((b"XTRA", b"\x01\x02\x03"), (b"MTrk", events)))
    assert song.notes == [Note(0.0, 1.0, 60, 100, 0)]
    assert song.programs == {}
    assert song.volumes == {}


def test_smpte_timing_is_refused() -> None:
    with pytest.raises(MidiError, match="SMPTE"):
        read(midi_file(per_beat=0xE728))
