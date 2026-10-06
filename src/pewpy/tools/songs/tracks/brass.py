"""The brass stabs."""

from pewpy.tools.songs.band import BRASS
from pewpy.tools.songs.writer import Writer, near


def brass(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...]) -> None:
    """Write brass stabs over `bars` bars of a chord."""
    for bar in range(bars):
        for beat, length in ((0, 0.4), (1.5, 0.4), (3, 0.9)) if bar % 2 == 0 else ((0, 0.4), (2.5, 1.3)):
            for step in shape[:3]:
                writer.add(BRASS, start + bar * 4 + beat, length, near(root, 60) + step, 104)
