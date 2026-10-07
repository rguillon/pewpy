"""Reading a standard MIDI file."""

import struct
from dataclasses import dataclass, field

from pewpy.audio.midi.song import MidiError, Note, Song


class _Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.at = 0

    def take(self, count: int) -> bytes:
        if self.at + count > len(self.data):
            raise MidiError.truncated()
        chunk = self.data[self.at : self.at + count]
        self.at += count
        return chunk

    def byte(self) -> int:
        return self.take(1)[0]

    def variable(self) -> int:
        value = 0
        while True:
            byte = self.byte()
            value = (value << 7) | (byte & 0x7F)
            if not byte & 0x80:
                return value

    @property
    def done(self) -> bool:
        return self.at >= len(self.data)


@dataclass
class _Parsed:
    notes: list[Note] = field(default_factory=list)
    programs: dict[int, int] = field(default_factory=dict)
    volumes: dict[int, int] = field(default_factory=dict)
    tempos: list[tuple[float, float]] = field(default_factory=list)
    loop: float = 0.0
    title: str = ""
    playing: dict[tuple[int, int], tuple[float, int]] = field(default_factory=dict)  # (channel, pitch) -> start

    def note_off(self, channel: int, pitch: int, beat: float) -> None:
        started = self.playing.pop((channel, pitch), None)
        if started is not None and beat > started[0]:
            self.notes.append(Note(started[0], beat - started[0], pitch, started[1], channel))


def _meta(reader: _Reader, beat: float, parsed: _Parsed) -> bool:
    """Read a meta event (after its 0xFF); return False at the end of the track."""
    kind = reader.byte()
    data = reader.take(reader.variable())
    if kind == 0x51:
        parsed.tempos.append((beat, 60_000_000 / int.from_bytes(data, "big")))
    elif kind == 0x06 and data == b"loop":
        parsed.loop = beat
    elif kind == 0x03 and not parsed.title:
        parsed.title = data.decode("utf-8", "replace")
    return kind != 0x2F


def _channel_message(reader: _Reader, status: int, data1: int, beat: float, parsed: _Parsed) -> None:
    kind, channel = status & 0xF0, status & 0x0F
    if kind in (0xC0, 0xD0):  # program change, channel pressure: one data byte
        if kind == 0xC0:
            parsed.programs[channel] = data1
        return
    data2 = reader.byte()
    if kind == 0x90 and data2 > 0:
        parsed.note_off(channel, data1, beat)  # a note played again before it ended
        parsed.playing[channel, data1] = (beat, data2)
    elif kind in (0x80, 0x90):
        parsed.note_off(channel, data1, beat)
    elif kind == 0xB0 and data1 == 7:
        parsed.volumes[channel] = data2


def _read_track(reader: _Reader, per_beat: int, parsed: _Parsed) -> None:
    tick = 0
    status = 0
    while not reader.done:
        tick += reader.variable()
        beat = tick / per_beat
        first = reader.byte()
        if first == 0xFF:
            if not _meta(reader, beat, parsed):
                return
        elif first in (0xF0, 0xF7):  # system exclusive
            reader.take(reader.variable())
        elif first & 0x80:
            status = first
            _channel_message(reader, status, reader.byte(), beat, parsed)
        else:  # running status: the same kind of message as the last one
            _channel_message(reader, status, first, beat, parsed)


def read(data: bytes) -> Song:
    """Read a standard MIDI file (timed in ticks per beat) as a Song: its tracks merged."""
    reader = _Reader(data)
    if reader.take(4) != b"MThd":
        raise MidiError.not_midi()
    size = struct.unpack(">I", reader.take(4))[0]
    _, track_count, per_beat = struct.unpack(">HHH", reader.take(6))
    reader.take(size - 6)
    if per_beat & 0x8000:
        raise MidiError.smpte()
    parsed = _Parsed()
    for _ in range(track_count):
        kind = reader.take(4)
        length = struct.unpack(">I", reader.take(4))[0]
        chunk = reader.take(length)
        if kind == b"MTrk":
            _read_track(_Reader(chunk), per_beat, parsed)
            parsed.playing.clear()  # notes left on at the end of a track are dropped
    tempos = sorted(parsed.tempos) or [(0.0, 120.0)]
    first = tempos[0][1] if tempos[0][0] == 0 else 120.0
    return Song(
        tempo=first,
        notes=sorted(parsed.notes, key=lambda note: (note.start, note.channel, note.pitch)),
        programs=parsed.programs,
        volumes=parsed.volumes,
        tempo_changes=[(beat, bpm) for beat, bpm in tempos if beat > 0],
        length=parsed.loop,
        title=parsed.title,
    )
