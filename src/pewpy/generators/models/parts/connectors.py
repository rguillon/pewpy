"""The connectors: beams joining a ship's hulls, made to any length: girders, lattice trusses, tubes, pipe bundles.

A connector runs across the ship, from its inner end on x = 0 out to the left (x < 0), its middle on y = 0 and z = 0;
mirrored, it runs to the right. The catalog shows each style in a few lengths.
"""

from collections.abc import Callable
from functools import cache

from pewpy.generators.models.parts.part import Part, Sketch

STYLES = {  # what each style is
    "girder": "a box girder, plated, riveted",
    "truss": "a lattice truss: two rails, braced across",
    "tube": "a round tube, banded",
    "pipes": "a bundle of pipes on brackets",
}
LENGTHS = (6, 12, 24)  # the catalog's


@cache
def connector_at(style: str, length: int, thick: int = 1) -> Part:
    """Build a connector of a style, `length` cubes long, `thick` cubes from its middle to its sides (1 or more)."""
    sketch = Sketch()
    span = range(-length + 1, 1)
    DRAWN[style](sketch, span, thick)
    what = STYLES[style]
    return sketch.part(f"{style}, {length} long", "connector", "connector", f"A connector, {what}: {length} long.")


def _girder(sketch: Sketch, span: range, thick: int) -> None:
    """Draw a box girder: a dark square beam, its top plated, a rivet line every few cubes."""
    for x in span:
        sketch.box(x, x, -thick, thick, -thick, thick, "N", mirror=False)
        sketch.box(x, x, -thick, thick, thick, thick, "H" if x % 4 else "k", mirror=False)


def _truss(sketch: Sketch, span: range, thick: int) -> None:
    """Draw a lattice truss: two rails, bracing zigzagging between them unbroken, rungs across."""
    period = 4 * thick
    before = -thick
    for x in span:
        sketch.box(x, x, -thick, -thick, 0, 0, "N", mirror=False)
        sketch.box(x, x, thick, thick, 0, 0, "N", mirror=False)
        phase = x % period
        brace = -thick + (phase if phase <= 2 * thick else period - phase)
        for y in range(min(brace, before), max(brace, before) + 1):
            sketch.put(x, y, 0, "k", mirror=False)
        before = brace
        if phase == 0:
            sketch.box(x, x, -thick, thick, 0, 0, "W", mirror=False)  # a rung across


def _tube(sketch: Sketch, span: range, thick: int) -> None:
    """Draw a round tube, a darker band every few cubes."""
    for x in span:
        for y in range(-thick, thick + 1):
            for z in range(-thick, thick + 1):
                if y * y + z * z <= thick * thick + thick:
                    sketch.put(x, y, z, "N" if x % 5 == 0 else "h", mirror=False)


def _pipes(sketch: Sketch, span: range, thick: int) -> None:
    """Draw a bundle of pipes side by side, brackets holding them every few cubes."""
    for x in span:
        for y in range(-thick, thick + 1, 2):
            sketch.put(x, y, 0, "r", mirror=False)
        if x % 4 == 0:
            sketch.box(x, x, -thick, thick, -1, 0, "N", mirror=False)


DRAWN: dict[str, Callable[[Sketch, range, int], None]] = {
    "girder": _girder,
    "truss": _truss,
    "tube": _tube,
    "pipes": _pipes,
}


def connectors() -> list[Part]:
    """Return the catalog's connectors: each style in a few lengths."""
    return [connector_at(style, length) for style in STYLES for length in LENGTHS]
