"""The arpeggio."""

from pewpy.generators.music.band import ARP
from pewpy.generators.music.harmony import ARPS
from pewpy.generators.music.writer import Writer, near


def arp(writer: Writer, start: float, bars: int, root: int, shape: tuple[int, ...], velocity: int) -> None:
    """Write the arpeggio over `bars` bars of a chord."""
    tones = [near(root, 64) + step for step in shape[:3]]
    tones.append(tones[0] + 12)
    pattern = ARPS[writer.plan.arp]
    for step in range(bars * 16):
        lift = 12 if (step // 16) % 2 and writer.plan.arp != "pedal" else 0
        accent = 18 if step % 4 == 0 else 0
        writer.add(ARP, start + step / 4, 0.2, tones[pattern[step % len(pattern)]] + lift, velocity + accent)
