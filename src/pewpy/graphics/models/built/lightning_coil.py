"""The player's lightning gun."""

from panda3d.core import NodePath, Vec3

from pewpy import config
from pewpy.graphics.models.mesh.builder import MeshBuilder


def lightning_coil_model() -> NodePath:
    """Make the lightning gun, sitting on the ship: a glowing violet orb."""
    size = config.MODEL_VOXEL
    mesh = MeshBuilder()
    mesh.ellipsoid(Vec3(0, 0, 0), Vec3(2.5 * size, 2.5 * size, 2.5 * size), (0.8, 0.6, 1.0, 1), rings=6, segments=10)
    orb = NodePath(mesh.build("lightning_coil"))
    orb.setLightOff()
    orb.setShaderOff()
    return orb
