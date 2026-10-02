"""Writing a song as a standard MIDI file."""

import struct

from pewpy.audio.midi.song import TICKS_PER_BEAT, Song


def _variable(value: int) -> bytes:
    """Write a MIDI variable-length number: 7 bits per byte, the high bit set on all but the last."""
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(out))


def _ticks(beats: float) -> int:
    return round(beats * TICKS_PER_BEAT)


def _track(events: list[tuple[int, int, bytes]]) -> bytes:
    """Write a track chunk from (tick, order, message) events; at the same tick, lower `order` first."""
    data = bytearray()
    now = 0
    for tick, _, message in sorted(events, key=lambda event: (event[0], event[1])):
        data += _variable(tick - now) + message
        now = tick
    data += _variable(0) + b"\xff\x2f\x00"  # end of track
    return b"MTrk" + struct.pack(">I", len(data)) + bytes(data)


def _tempo_message(bpm: float) -> bytes:
    return b"\xff\x51\x03" + struct.pack(">I", round(60_000_000 / bpm))[1:]


def write(song: Song, name: str = "") -> bytes:
    """`song` as a format 1 MIDI file: a tempo track, then a track per channel."""
    conductor: list[tuple[int, int, bytes]] = [(0, 0, _tempo_message(song.tempo))]
    if name:
        text = name.encode()
        conductor.append((0, 0, b"\xff\x03" + _variable(len(text)) + text))
    conductor += [(_ticks(beat), 0, _tempo_message(bpm)) for beat, bpm in song.tempo_changes]
    conductor.append((_ticks(song.beats), 1, b"\xff\x06\x04loop"))  # a marker where the song loops
    tracks = [_track(conductor)]
    channels = sorted({note.channel for note in song.notes} | set(song.programs))
    for channel in channels:
        events: list[tuple[int, int, bytes]] = []
        if channel in song.programs:
            events.append((0, 0, bytes((0xC0 | channel, song.programs[channel]))))
        if channel in song.volumes:
            events.append((0, 0, bytes((0xB0 | channel, 7, song.volumes[channel]))))
        for note in song.notes:
            if note.channel != channel:
                continue
            start = _ticks(note.start)
            end = max(start + 1, _ticks(note.start + note.length))
            events.append((start, 2, bytes((0x90 | channel, note.pitch, note.velocity))))
            events.append((end, 1, bytes((0x80 | channel, note.pitch, 0))))  # before a note starting there
        tracks.append(_track(events))
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TICKS_PER_BEAT)
    return header + b"".join(tracks)
