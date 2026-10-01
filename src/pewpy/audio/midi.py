"""Standard MIDI files: songs as notes, read and written. No Panda3D.

Only what songs need: notes, the instrument of each channel (program change), the channel volume (controller 7)
and the tempo (with changes). Channel 9 (the tenth) holds the drums, as in General MIDI.
"""

import struct
from dataclasses import dataclass, field

DRUMS = 9  # the General MIDI drum channel
TICKS_PER_BEAT = 480


@dataclass(frozen=True)
class Note:
    start: float  # beats
    length: float  # beats
    pitch: int  # MIDI note number, 60 = middle C
    velocity: int = 100  # 1 to 127
    channel: int = 0


@dataclass
class Song:
    tempo: float  # beats per minute
    notes: list[Note] = field(default_factory=list)
    programs: dict[int, int] = field(default_factory=dict)  # channel -> General MIDI program (0 to 127)
    volumes: dict[int, int] = field(default_factory=dict)  # channel -> volume (0 to 127, 100 when unset)
    tempo_changes: list[tuple[float, float]] = field(default_factory=list)  # (beat, bpm) after the start
    length: float = 0.0  # beats; the song loops from here (0: the end of its last note)

    @property
    def beats(self) -> float:
        return self.length or max((note.start + note.length for note in self.notes), default=0.0)

    def seconds(self, beat: float) -> float:
        """When `beat` is played, with the tempo changes."""
        time, at, tempo = 0.0, 0.0, self.tempo
        for change_beat, bpm in sorted(self.tempo_changes):
            if change_beat >= beat:
                break
            time += (change_beat - at) * 60.0 / tempo
            at, tempo = change_beat, bpm
        return time + (beat - at) * 60.0 / tempo

    @property
    def duration(self) -> float:
        """Seconds."""
        return self.seconds(self.beats)


class MidiError(ValueError):
    @classmethod
    def not_midi(cls) -> "MidiError":
        return cls("not a standard MIDI file")

    @classmethod
    def truncated(cls) -> "MidiError":
        return cls("the MIDI file ends too soon")

    @classmethod
    def smpte(cls) -> "MidiError":
        return cls("SMPTE timing isn't supported, only ticks per beat")


def _variable(value: int) -> bytes:
    """A MIDI variable-length number: 7 bits per byte, the high bit set on all but the last."""
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(out))


def _ticks(beats: float) -> int:
    return round(beats * TICKS_PER_BEAT)


def _track(events: list[tuple[int, int, bytes]]) -> bytes:
    """A track chunk from (tick, order, message) events; at the same tick, lower `order` first."""
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
    playing: dict[tuple[int, int], tuple[float, int]] = field(default_factory=dict)  # (channel, pitch) -> start

    def note_off(self, channel: int, pitch: int, beat: float) -> None:
        started = self.playing.pop((channel, pitch), None)
        if started is not None and beat > started[0]:
            self.notes.append(Note(started[0], beat - started[0], pitch, started[1], channel))


def _meta(reader: _Reader, beat: float, parsed: _Parsed) -> bool:
    """A meta event (after its 0xFF); False at the end of the track."""
    kind = reader.byte()
    data = reader.take(reader.variable())
    if kind == 0x51:
        parsed.tempos.append((beat, 60_000_000 / int.from_bytes(data, "big")))
    elif kind == 0x06 and data == b"loop":
        parsed.loop = beat
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
    )
