"""The cockpits: canopies, visors, bridges, domes and a slit on top; sensor eyes and a glass nose on the nose.

A canopy is glass (c) blown round over a dark coaming (N), highest towards its front, the light catching its top (C),
its frame's bows across its top (k), a fairing behind it running down into the hull. A bridge is an armored cab, a
band of windows round its front, a roof and a mast. The command tower stands beside its own middle: only lopsided ships
carry it.
"""

import math

from pewpy.generators.models.ships.parts.part import Part, Sketch

GLASS, GLINT, FRAME, COAMING = "c", "C", "k", "N"  # the frame dark, thin lines across the glass


def _envelope(share: float, peak: float) -> float:
    """Return how high a canopy is `share` of the way from its back to its front (1 at its `peak`, 0 at its ends)."""
    span = peak if share < peak else 1 - peak
    off = (share - peak) / span
    return math.sqrt(max(0.0, 1 - off * off))


def _glass(
    sketch: Sketch, back: int, long: int, half: float, tall: int, *, peak: float, bows: tuple[int, ...], x: int = 0
) -> None:
    """Blow a canopy's glass `long` rows from row `back`, `half` cubes each side of x at its widest, `tall` high.

    Over a coaming one cube wider; its frame's bows on the rows `bows` (counted from its back). Off the middle (`x`),
    a pair.
    """
    for row in range(long):
        envelope = _envelope((row + 0.5) / long, peak)
        wide, high = half * math.sqrt(envelope), max(1, round(tall * envelope**0.7))
        reach = round(wide)
        y = back + row
        sketch.box(x - reach - 1, x + reach + 1, y, y, 0, 0, COAMING)
        for dx in range(-reach, reach + 1):
            top = max(1, round(high * math.sqrt(max(0.0, 1 - (dx / (wide + 0.6)) ** 2))))
            for z in range(1, top + 1):
                char = GLASS
                if row in bows and z == top:
                    char = FRAME
                elif z == top and abs(dx) == min(1, reach) and long * 0.2 <= row < long * 0.75:
                    char = GLINT  # streaks of light along its top, each side of the middle
                sketch.put(x + dx, y, z, char, mirror=x != 0)


def _fairing(sketch: Sketch, long: int, half: float, tall: int) -> None:
    """Draw a fairing `long` rows behind a canopy, rising from the hull to its height, a spine along its top."""
    for row in range(long):
        share = (row + 1) / (long + 1)
        reach, high = round(half * 0.6 * share), max(1, round(tall * share))
        sketch.box(-reach - 1, reach + 1, row, row, 0, 0, COAMING)
        for z in range(1, high + 1):
            sketch.box(-reach, reach, row, row, z, z, "h")
        if row % 2:
            sketch.box(-reach, reach, row, row, high, high, "N")  # its plates' seams


def canopy(
    name: str,
    long: int,
    half: float,
    tall: int,
    *,
    peak: float = 0.6,
    bows: tuple[int, ...] = (),
    fairing: int = 0,
    description: str,
) -> Part:
    """Build a canopy: a fairing `fairing` rows long, then the glass (see `_glass`)."""
    sketch = Sketch()
    if fairing:
        _fairing(sketch, fairing, half, tall)
    _glass(sketch, fairing, long, half, tall, peak=peak, bows=bows)
    return sketch.part(name, "cockpit", "top", description)


def twin_canopy(name: str, long: int, gap: int) -> Part:
    """Build two narrow canopies side by side, `gap` cubes each side of the middle, a spine between them."""
    sketch = Sketch()
    _glass(sketch, 0, long, 0.6, 1, peak=0.6, bows=(1,), x=gap)
    sketch.box(-gap + 1, gap - 1, 0, long - 1, 0, 0, COAMING)
    sketch.box(0, 0, 0, long - 1, 1, 1, "h")
    return sketch.part(name, "cockpit", "top", f"Two canopies side by side, {long} cubes long.")


def visor(name: str, half: int, long: int) -> Part:
    """Build an armored hood, a wraparound visor across its front half, sloping down to the hull."""
    sketch = Sketch()
    glazed = long // 2 + 1  # the rows of glass
    sketch.box(-half - 1, half + 1, 0, long - 1, 0, 0, COAMING)
    sketch.box(-half, half, 0, long - glazed - 1, 1, 1, "h")
    sketch.box(-half, half, long - glazed - 1, long - glazed - 1, 1, 1, "N")  # the hood's edge
    sketch.box(-half, half, long - glazed, long - 2, 1, 1, GLASS)
    sketch.box(-half, half, long - 1, long - 1, 0, 0, GLASS)  # its front row lower: a slope
    sketch.box(-half - 1, -half - 1, long - glazed, long - 1, 0, 0, GLASS)  # wrapping round its sides
    sketch.box(1, 1, long - glazed, long - 2, 1, 1, GLINT)
    return sketch.part(name, "cockpit", "top", f"An armored hood, a visor {2 * half + 1} cubes across its front.")


def bridge(name: str, half: int, long: int, tall: int, *, deck: bool = False) -> Part:
    """Build an armored bridge: a cab, windows round its front, a roof, a mast with a light at its back.

    With a `deck`, it stands on a wider lower deck, plated.
    """
    sketch = Sketch()
    base = 0
    if deck:
        sketch.box(-half - 1, half + 1, 0, long, 0, 0, "N")
        sketch.box(-half - 1, half + 1, 0, long, 1, 1, "h")
        sketch.box(-half - 1, half + 1, long, long, 1, 1, "H")
        base = 2
    top = base + tall - 1
    sketch.box(-half, half, 0, long - 1, base, top, "h")
    sketch.box(-half, half, 0, long - 1, base, base, "N")
    sketch.box(-half, half, long - 1, long - 1, top, top, GLASS)  # the windows round its front
    sketch.box(-half, -half, long // 2, long - 1, top, top, GLASS)
    for x in range(-half + 1, half, 2):
        sketch.put(x, long - 1, top, "N")  # mullions
    sketch.put(0, long - 1, top, GLINT)
    sketch.box(-half + 1, half - 1, 0, long - 2, top + 1, top + 1, "S")  # the roof, its front edge glazed
    sketch.box(-half + 1, half - 1, long - 2, long - 2, top + 1, top + 1, GLASS)
    sketch.put(min(1, half - 1), long - 2, top + 1, GLINT)
    sketch.box(0, 0, 0, 0, top + 2, top + 3, "k")
    sketch.box(-1, 1, 0, 0, top + 3, top + 3, "k")
    sketch.put(0, 0, top + 4, "R")
    what = "on a lower deck" if deck else f"{tall} cubes high"
    return sketch.part(name, "cockpit", "top", f"An armored bridge {what}, windows round its front, a mast.")


def slit(name: str, long: int) -> Part:
    """Build an armored hump, a narrow slit of glass along its top."""
    sketch = Sketch()
    sketch.box(-2, 2, 0, long + 1, 0, 0, COAMING)
    sketch.box(-1, 1, 1, long, 1, 1, "H")
    sketch.box(0, 0, 2, long, 1, 1, GLASS)
    sketch.put(0, long - 1, 1, GLINT)
    sketch.box(-1, 1, long + 1, long + 1, 1, 1, "N")
    return sketch.part(name, "cockpit", "top", f"An armored hump, a slit of glass {long - 1} cubes long.")


def tower(name: str, tall: int) -> Part:
    """Build a command tower beside its own middle: a block, a cab with windows round it, a mast and a dish."""
    sketch = Sketch()
    sketch.box(0, 3, 0, 4, 0, 0, "N", mirror=False)
    sketch.box(0, 2, 0, 4, 1, tall - 1, "h", mirror=False)
    sketch.box(0, 2, 0, 4, tall, tall, GLASS, mirror=False)  # the cab's windows, all round
    sketch.box(1, 1, 1, 3, tall, tall, "h", mirror=False)
    sketch.put(1, 4, tall, GLINT, mirror=False)
    sketch.box(0, 2, 0, 4, tall + 1, tall + 1, "S", mirror=False)
    sketch.box(1, 1, 1, 1, tall + 2, tall + 3, "k", mirror=False)
    sketch.box(0, 2, 1, 1, tall + 3, tall + 3, "W", mirror=False)  # a dish
    sketch.put(1, 1, tall + 4, "R", mirror=False)
    return sketch.part(
        name, "cockpit", "top", f"A command tower off to one side, {tall + 4} cubes high (lopsided ships)."
    )


def eye(name: str, *, big: bool) -> Part:
    """Build a sensor eye on the nose: a dark rim, a glowing lens bulging out of it."""
    sketch = Sketch()
    if big:
        sketch.box(-2, 2, 0, 0, -1, 1, "N")
        sketch.box(-1, 1, 0, 0, -2, 2, "N")
        sketch.box(-1, 1, 1, 1, -1, 1, "R")
        sketch.box(-1, 1, 1, 1, 0, 0, "W")
        sketch.box(0, 0, 1, 1, -1, 1, "W")
        sketch.put(0, 1, 0, "R")
        sketch.put(0, 2, 0, "R")
    else:
        sketch.box(-1, 1, 0, 0, -1, 1, "N")
        sketch.box(0, 0, 1, 1, 0, 0, "R")
    return sketch.part(name, "cockpit", "nose", "A glowing sensor eye on the nose (no pilot).")


def glass_nose(name: str) -> Part:
    """Build a glazed nose: a cone of glass panes in a frame."""
    sketch = Sketch()
    sketch.box(-2, 2, 0, 0, -1, 1, "N")
    sketch.box(-1, 1, 0, 0, -2, 2, "N")
    sketch.box(-1, 1, 1, 2, -1, 1, GLASS)
    sketch.box(-1, 1, 1, 1, 1, 1, FRAME)
    sketch.box(1, 1, 2, 2, 1, 1, GLINT)
    sketch.box(0, 0, 3, 3, -1, 0, GLASS)
    sketch.put(0, 4, 0, "N")
    return sketch.part(name, "cockpit", "nose", "A glazed nose: panes of glass in a frame.")


def cockpits() -> list[Part]:
    """Return every cockpit."""
    return [
        canopy("bubble, small", 3, 0.8, 1, fairing=1, description="A small bubble canopy, a fairing behind it."),
        canopy("bubble", 5, 1.2, 2, bows=(1,), fairing=2, description="A bubble canopy, its windscreen framed."),
        canopy("bubble, tall", 6, 1.5, 3, bows=(2,), fairing=3, description="A tall bubble canopy, high above."),
        canopy("bubble, wide", 6, 2.4, 2, bows=(2,), fairing=2, description="A wide bubble canopy, two seats."),
        canopy("canopy, short", 4, 0.6, 1, bows=(1,), fairing=1, description="A short narrow canopy."),
        canopy("canopy", 6, 1.0, 2, peak=0.45, bows=(2, 4), fairing=2, description="A framed canopy, three panes."),
        canopy("canopy, long", 9, 1.0, 2, peak=0.5, bows=(2, 5, 7), fairing=3, description="A long framed canopy."),
        canopy("tandem canopy", 9, 1.4, 2, peak=0.5, bows=(1, 4, 7), fairing=2, description="Two seats in a row."),
        twin_canopy("twin canopy", 5, 2),
        visor("visor, narrow", 1, 4),
        visor("visor", 2, 5),
        visor("visor, wide", 3, 5),
        bridge("bridge, small", 1, 3, 2),
        bridge("bridge", 2, 4, 2),
        bridge("bridge, tall", 2, 5, 3),
        bridge("bridge on a deck", 2, 4, 2, deck=True),
        canopy("glass dome", 3, 1.2, 1, peak=0.5, bows=(1,), description="A small glass dome, framed across."),
        canopy("glass dome, big", 5, 2.2, 2, peak=0.5, bows=(2,), description="A glass dome, framed across."),
        slit("armored slit", 5),
        tower("command tower", 2),
        tower("command tower, tall", 4),
        eye("sensor eye", big=False),
        eye("sensor eye, big", big=True),
        glass_nose("glass nose"),
    ]
