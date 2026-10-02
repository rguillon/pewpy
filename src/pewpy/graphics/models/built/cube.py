"""The plain cube (bullets)."""

from panda3d.core import GeomNode, Vec3

from pewpy.graphics.models.mesh.builder import MeshBuilder


def make_cube(name: str = "cube") -> GeomNode:
    """Make a plain 1 x 1 x 1 cube centered on the origin (used for bullets)."""
    mesh = MeshBuilder()
    mesh.box(Vec3(0, 0, 0), Vec3(1, 1, 1), (1, 1, 1, 1))
    return mesh.build(name)
