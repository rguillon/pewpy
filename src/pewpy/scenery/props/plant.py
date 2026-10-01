"""Process plants: furnace halls with glowing windows, roofs flat or sawtooth, chimneys or fans on top, sometimes
a lower annex."""

import random

from pewpy.scenery.params import PropColors
from pewpy.scenery.props.mesh import FURNACE, METAL, PLAIN, ROOFING, PropMesh, footprint, varied
from pewpy.scenery.settlement import Prop


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    x0, x1, y0, y1 = footprint(prop)
    top = prop.base + prop.height
    walls, roof = varied(rng, c.plant_walls), varied(rng, c.plant_roof)
    if rng.random() < 0.3 and (x1 - x0) > 0.06:  # a lower annex along one side
        cut = x0 + (x1 - x0) * rng.uniform(0.6, 0.75)
        mesh.box(
            cut, x1, y0, y1, prop.base, prop.base + prop.height * 0.55, walls, FURNACE, top=roof, top_material=ROOFING
        )
        x1 = cut
    mesh.box(x0, x1, y0, y1, prop.base, top, walls, FURNACE, top=roof, top_material=ROOFING)
    if rng.random() < 0.35:
        _sawtooth(mesh, (x0, x1, y0, y1), top, roof, c)
    roll = rng.random()
    if roll < 0.5:  # small chimneys
        for _ in range(rng.randint(1, 3)):
            cx, cy = rng.uniform(x0 + 0.015, x1 - 0.015), rng.uniform(y0 + 0.015, y1 - 0.015)
            mesh.cylinder(cx, cy, 0.007, top, top + rng.uniform(0.03, 0.07), c.stack, PLAIN, segments=8)
    elif roll < 0.85:  # roof fans
        for _ in range(rng.randint(2, 4)):
            cx, cy = rng.uniform(x0 + 0.01, x1 - 0.01), rng.uniform(y0 + 0.01, y1 - 0.01)
            mesh.cylinder(cx, cy, 0.007, top, top + 0.006, c.roof_unit, METAL, segments=10)
            mesh.disc(cx, cy, 0.005, top + 0.0065, c.stack, PLAIN, segments=10)


def _sawtooth(
    mesh: PropMesh,
    footprint_: tuple[float, float, float, float],
    top: float,
    roof: tuple[float, float, float],
    c: PropColors,
) -> None:
    """A row of sloped roof lights across the hall."""
    x0, x1, y0, y1 = footprint_
    teeth = max(2, int((y1 - y0) / 0.025))
    step = (y1 - y0) / teeth
    for index in range(teeth):
        a, b = y0 + index * step, y0 + (index + 1) * step
        rise = step * 0.6
        mesh.face([(x0, a, top), (x1, a, top), (x1, b, top + rise), (x0, b, top + rise)], roof, ROOFING)
        mesh.quad(
            [(x0, b, top), (x1, b, top), (x1, b, top + rise), (x0, b, top + rise)], (0.0, 1.0, 0.0), c.glass, METAL
        )
