"""The engines: nozzles, blocks and clusters on a hull's tail; nacelles (pods) beside it, under a wing or on its tip.

Each flames out of its back (y = 0): the nozzle's mouth is dark ("o"), or glowing for an ion engine.
"""

from pewpy.generators.models.ships.parts.part import Part, Sketch

# Nozzle cross-sections: (x, z) offsets from the nozzle's middle, by size. "o" is the mouth, "N" the housing round
# it, "D" its darker underside.
SECTIONS: dict[int, dict[tuple[int, int], str]] = {
    1: {(0, 0): "o"},
    2: {(0, 0): "o", (-1, 0): "N", (1, 0): "N", (0, 1): "N", (0, -1): "D"},
    3: {
        **{(x, z): "o" for x in (-1, 0, 1) for z in (-1, 0, 1) if abs(x) + abs(z) < 2},
        **{(x, z): "N" for x in (-2, 2) for z in (-1, 0, 1)},
        **{(x, z): "N" for x in (-1, 0, 1) for z in (2,)},
        **{(x, z): "D" for x in (-1, 0, 1) for z in (-2,)},
    },
    4: {
        **{(x, z): "o" for x in range(-2, 3) for z in range(-2, 3) if x * x + z * z <= 5},
        **{(x, z): "N" for x in range(-3, 4) for z in range(4) if 6 <= x * x + z * z <= 11},
        **{(x, z): "D" for x in range(-3, 4) for z in range(-3, 0) if 6 <= x * x + z * z <= 11},
    },
}
SIZE_NAMES = {1: "tiny", 2: "small", 3: "medium", 4: "big"}


def _section(sketch: Sketch, y: int, size: int, x: int = 0, z: int = 0, *, mouth: bool, glow: bool = False) -> None:
    """Draw a nozzle's cross-section on row y around (x, z): its mouth, or (behind it) its housing."""
    for (dx, dz), char in SECTIONS[size].items():
        paint = (("G" if glow else "o") if mouth else "N") if char == "o" else char
        sketch.put(x + dx, y, z + dz, paint, mirror=x != 0)


def nozzle(size: int, depth: int) -> Part:
    """Build a tail nozzle of a size, its housing `depth` cubes long."""
    sketch = Sketch()
    for y in range(depth):
        _section(sketch, y, size, mouth=y == 0)
    sketch.nozzle(0, 0, 0, size + 0.6)
    length = "long" if depth > 2 else "short"
    return sketch.part(
        f"tail nozzle, {SIZE_NAMES[size]}, {length}", "engine", "tail", f"One nozzle on the tail, size {size}."
    )


def block(name: str, size: int, xs: list[int], zs: list[int], depth: int, description: str) -> Part:
    """Build a housing holding nozzles of a size at each (x, z) of `xs` and `zs` (mirrored across the middle)."""
    sketch = Sketch()
    reach = max(xs) + size
    tall = max(abs(z) for z in zs) + (size + 1) // 2
    sketch.box(-reach, reach, 0, depth - 1, -tall, tall, "N")
    sketch.box(-reach, reach, depth - 1, depth - 1, tall, tall, "H")
    for x in xs:
        for z in zs:
            for y in range(depth):
                _section(sketch, y, size, x, z, mouth=y == 0)
            sketch.nozzle(x, 0, z, size + 0.6)
    return sketch.part(name, "engine", "tail", description)


def slot(name: str, half: int) -> Part:
    """Build a flat slot nozzle, `2 * half + 1` cubes wide and one high."""
    sketch = Sketch()
    sketch.box(-half - 1, half + 1, 0, 2, -1, 1, "N")
    sketch.box(-half, half, 0, 0, 0, 0, "o")
    sketch.box(-half - 1, half + 1, 2, 2, 1, 1, "H")
    sketch.nozzle(0, 0, 0, 2 * half + 1.0)
    return sketch.part(name, "engine", "tail", f"A flat slot nozzle, {2 * half + 1} cubes wide.")


def ion(name: str, mount: str, long: int) -> Part:
    """Build an ion engine: a round housing in bands, its mouth glowing."""
    sketch = Sketch()
    sketch.rod(0, long - 1, 2, "N")
    for y in range(1, long - 1, 2):
        sketch.rod(y, y, 2, "H")
    _section(sketch, 0, 3, mouth=True, glow=True)
    sketch.box(0, 0, long - 1, long - 1, 0, 0, "k")
    sketch.nozzle(0, 0, 0, 3.4)
    where = "on the tail" if mount == "tail" else "in a pod"
    return sketch.part(name, "engine", mount, f"An ion engine {where}, its mouth glowing.")


def nacelle(size: int, length: int) -> Part:
    """Build an engine pod `length` cubes long: its nozzle at the back, plated bands, an intake at its front."""
    sketch = Sketch()
    for y in range(length):
        for (dx, dz), char in SECTIONS[size].items():
            if y == 0:
                paint = char
            elif y == length - 1:
                paint = "k" if char == "o" else "H"  # the intake
            else:
                paint = "D" if char == "D" else ("h" if y % 3 else "H")
            sketch.put(dx, y, dz, paint)
    sketch.nozzle(0, 0, 0, size + 0.4)
    long = "long" if length > 6 else "short"
    return sketch.part(
        f"nacelle, {SIZE_NAMES[size]}, {long}", "engine", "pod", f"An engine pod {length} cubes long, size {size}."
    )


def afterburner(name: str, long: int) -> Part:
    """Build an afterburner can: a long round nozzle, a ring of the accent near its mouth."""
    sketch = Sketch()
    sketch.rod(0, long - 1, 1.5, "N")
    sketch.rod(2, 2, 1.5, "p")
    for y in range(4, long, 2):
        sketch.rod(y, y, 1.5, "H")
    sketch.box(0, 0, 0, 0, -1, 1, "o")
    sketch.box(-1, 1, 0, 0, 0, 0, "o")
    sketch.nozzle(0, 0, 0, 3.0)
    return sketch.part(name, "engine", "tail", f"An afterburner can, {long} cubes long.")


def engines() -> list[Part]:
    """Return every engine."""
    return [
        *(nozzle(size, depth) for size in SECTIONS for depth in (2, 4)),
        block("twin block", 2, [2], [0], 3, "Two small nozzles side by side in one housing."),
        block("twin block, big", 3, [3], [0], 4, "Two medium nozzles side by side in one housing."),
        block("triple block", 1, [0, 2], [0], 3, "Three tiny nozzles in a row."),
        block("quad cluster", 1, [1], [-1, 1], 3, "Four tiny nozzles in a square."),
        block("quad cluster, big", 2, [2], [-2, 2], 3, "Four small nozzles in a square."),
        slot("slot nozzle, narrow", 1),
        slot("slot nozzle", 2),
        slot("slot nozzle, wide", 4),
        ion("ion engine", "tail", 4),
        afterburner("afterburner", 5),
        afterburner("afterburner, long", 8),
        *(nacelle(size, length) for size in (1, 2, 3) for length in (5, 9)),
        nacelle(4, 12),
        ion("ion pod", "pod", 7),
    ]
