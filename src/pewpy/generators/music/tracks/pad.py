"""The pad: the chords, held."""

from pewpy.generators.music.band import PAD
from pewpy.generators.music.writer import Writer, voice


def pad(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...], velocity: int) -> None:
    """Write the pad holding a chord for `bars` bars."""
    writer.voicing = voice(writer, root, shape)
    for pitch in writer.voicing:
        writer.add(PAD, start, bars * 4 - 0.05, pitch, velocity)
