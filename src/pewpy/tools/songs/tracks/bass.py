"""The bass line."""

from pewpy.tools.songs.band import BASS
from pewpy.tools.songs.writer import Writer, near


def bass(writer: Writer, start: float, bars: int, root: int) -> None:
    """Write the bass line over `bars` bars of a chord."""
    low = near(root, 38)
    style = writer.plan.bass
    for bar in range(bars):
        at = start + bar * 4
        last = bar == bars - 1
        if style == "sixteenths":
            for step in range(16):
                octave = 12 if step % 8 == 6 else 0
                writer.add(BASS, at + step / 4, 0.22, low + octave, 112 if step % 4 == 0 else 88)
        elif style == "gallop":
            for beat in range(4):
                for offset, length in ((0, 0.5), (0.5, 0.25), (0.75, 0.25)):
                    up = 12 if (beat == 3 and offset == 0.5 and last) else 0
                    writer.add(BASS, at + beat + offset, length * 0.9, low + up, 110 if offset == 0 else 85)
        else:
            for step in range(8):
                up = 12 if step in (3, 7) else 0
                writer.add(BASS, at + step / 2, 0.42, low + up, 112 if step % 2 == 0 else 92)
