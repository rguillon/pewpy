"""The drums: hi-hats, kick and snare, fills and crashes."""

from pewpewdev.tools.songs.band import CLOSED_HAT, CRASH, KICK, OPEN_HAT, SNARE, TOMS
from pewpewdev.tools.songs.writer import Writer
from pewpy.audio.midi import DRUMS


def hats(writer: Writer, at: float, busy: bool, until: float) -> None:
    style = writer.plan.drums
    count = 16 if busy and style != "half" else 8
    for step in range(count):
        when = step * 4 / count
        if when >= until:
            break
        open_hat = style == "four" and when % 1 == 0.5
        writer.add(DRUMS, at + when, 0.1, OPEN_HAT if open_hat else CLOSED_HAT, 80 if when % 1 == 0 else 58)


def drums(writer: Writer, start: float, bars: int, busy: bool, fill: bool, crash: bool) -> None:
    style = writer.plan.drums
    kicks = {"half": (0, 2.5), "standard": (0, 1.5, 2), "four": (0, 1, 2, 3)}[style]
    snares = (2,) if style == "half" else (1, 3)
    if crash:
        writer.add(DRUMS, start, 0.5, CRASH, 105)
    for bar in range(bars):
        at = start + bar * 4
        until = 2 if fill and bar == bars - 1 else 4  # the fill takes the last two beats
        for beat in kicks:
            if beat < until:
                writer.add(DRUMS, at + beat, 0.25, KICK, 120 if beat == 0 else 108)
        for beat in snares:
            if beat < until:
                writer.add(DRUMS, at + beat, 0.25, SNARE, 118)
        hats(writer, at, busy, until)
        if until == 2:  # down the toms, two hits each
            for step in range(8):
                writer.add(DRUMS, at + 2 + step / 4, 0.25, TOMS[min(step // 2 + step % 2, 5)], 96 + step * 3)
