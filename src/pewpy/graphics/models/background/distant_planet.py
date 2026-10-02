"""A distant planet."""

import random

from panda3d.core import NodePath, Vec3

from pewpy.graphics.models.colors import mottle
from pewpy.graphics.models.mesh.builder import MeshBuilder
from pewpy.graphics.models.types import Color


def distant_planet_model(colors: tuple[Color, ...], seed: int = 7) -> NodePath:
    """A big voxel planet with muted bands of `colors`; fits the unit box."""
    radius = 9
    rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
    band_colors = [rng.choice(colors) for _ in range(2 * radius + 1)]
    cells = {}
    for column in range(-radius, radius + 1):
        for row in range(-radius, radius + 1):
            for layer in range(-radius, radius + 1):
                if column * column + row * row + layer * layer <= radius * radius + radius:
                    cell = (column, row, layer)
                    cells[cell] = mottle(band_colors[row + radius], cell, 0.12)
    mesh = MeshBuilder()
    mesh.cells(cells, 1 / (2 * radius + 1), Vec3(0, 0, 0))
    return NodePath(mesh.build("distant_planet"))
