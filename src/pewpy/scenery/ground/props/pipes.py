"""Pipe racks: three to six pipes of different sizes (some in another metal) on supports.

Sometimes a loop rises over the rack.
"""

import random

from pewpy.scenery.ground.props.mesh import METAL, PLAIN, PropMesh, footprint
from pewpy.scenery.ground.settlement import Prop
from pewpy.scenery.params import PropColors


def build(mesh: PropMesh, rng: random.Random, prop: Prop, c: PropColors) -> None:
    """Build a pipe rack."""
    x0, x1, y0, y1 = footprint(prop)
    z0, height = prop.base, prop.height
    along_y = (y1 - y0) > (x1 - x0)
    length = (y1 - y0) if along_y else (x1 - x0)
    across = (x0, x1) if along_y else (y0, y1)
    count = rng.randint(3, 6)
    for index in range(count):
        offset = across[0] + (across[1] - across[0]) * (index + 0.5) / count
        radius = rng.uniform(0.003, 0.007)
        color = rng.choice(c.refinery_metals) if rng.random() < 0.3 else c.pipe
        _pipe(mesh, along_y, offset, (x0, y0), z0 + height, length, radius, color)
    step = 0.06
    for index in range(int(length / step) + 1):  # supports
        at = index * step
        if along_y:
            mesh.box(x0, x1, y0 + at, y0 + at + 0.004, z0, z0 + height, c.pipe, PLAIN)
        else:
            mesh.box(x0 + at, x0 + at + 0.004, y0, y1, z0, z0 + height, c.pipe, PLAIN)
    if rng.random() < 0.4 and length > 0.1:  # an expansion loop rising over the rack
        at = rng.uniform(0.3, 0.7) * length
        offset = across[0] + (across[1] - across[0]) * 0.5 / count
        for dz in (0.0, 0.025):
            if along_y:
                mesh.box(
                    offset - 0.003,
                    offset + 0.003,
                    y0 + at - 0.02,
                    y0 + at + 0.02,
                    z0 + height + dz,
                    z0 + height + dz + 0.005,
                    c.pipe,
                    METAL,
                )
            else:
                mesh.box(
                    x0 + at - 0.02,
                    x0 + at + 0.02,
                    offset - 0.003,
                    offset + 0.003,
                    z0 + height + dz,
                    z0 + height + dz + 0.005,
                    c.pipe,
                    METAL,
                )


def _pipe(
    mesh: PropMesh,
    along_y: bool,
    offset: float,
    start: tuple[float, float],
    z: float,
    length: float,
    radius: float,
    color: tuple[float, float, float],
) -> None:
    """Add a pipe lying along the rack: a cylinder built upright, then turned over by swapping axes."""
    first = len(mesh.vertices)
    mesh.cylinder(0.0, 0.0, radius, 0.0, length, color, METAL, segments=8)
    x0, y0 = start
    for vertices in mesh.vertices[first:]:
        px, py, pz = vertices[:, 0].copy(), vertices[:, 1].copy(), vertices[:, 2].copy()
        nx, ny, nz = vertices[:, 3].copy(), vertices[:, 4].copy(), vertices[:, 5].copy()
        if along_y:
            vertices[:, 0], vertices[:, 1], vertices[:, 2] = offset + px, y0 + pz, z + py
            vertices[:, 3], vertices[:, 4], vertices[:, 5] = nx, nz, ny
        else:
            vertices[:, 0], vertices[:, 1], vertices[:, 2] = x0 + pz, offset + px, z + py
            vertices[:, 3], vertices[:, 4], vertices[:, 5] = nz, nx, ny
