"""The pad: the chords, held."""

from pewpewdev.tools.songs.band import PAD
from pewpewdev.tools.songs.writer import Writer, voice


def pad(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...], velocity: int) -> None:
    writer.voicing = voice(writer, root, shape)
    for pitch in writer.voicing:
        writer.add(PAD, start, bars * 4 - 0.05, pitch, velocity)
