"""The pad: the chords, held."""

from pewpy.makers.songs.band import PAD
from pewpy.makers.songs.writer import Writer, voice


def pad(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...], velocity: int) -> None:
    """Write the pad holding a chord for `bars` bars."""
    writer.voicing = voice(writer, root, shape)
    for pitch in writer.voicing:
        writer.add(PAD, start, bars * 4 - 0.05, pitch, velocity)
