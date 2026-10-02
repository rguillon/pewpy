"""Asteroids."""

import random

from panda3d.core import NodePath, Vec3

from pewpy.graphics.models.colors import mottle
from pewpy.graphics.models.mesh.builder import MeshBuilder
from pewpy.graphics.models.types import Color


def rock_model(shape: int, colors: tuple[Color, ...]) -> NodePath:
    """A lumpy voxel asteroid of `colors`, the same for the same `shape`; fits the unit box."""
    rng = random.Random(shape)  # noqa: S311 - visual randomness, not cryptography
    radius = 3
    stretch = Vec3(rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0))
    cells = {}
    for column in range(-radius, radius + 1):
        for row in range(-radius, radius + 1):
            for layer in range(-radius, radius + 1):
                distance = Vec3(column / stretch.x, row / stretch.z, layer / stretch.y).length()
                if distance <= radius + rng.uniform(-0.6, 0.4):
                    cell = (column, row, layer)
                    cells[cell] = mottle(rng.choice(colors), cell, 0.15)
    mesh = MeshBuilder()
    mesh.cells(cells, 1 / (2 * radius + 1), Vec3(0, 0, 0))
    return NodePath(mesh.build(f"rock_{shape}"))
