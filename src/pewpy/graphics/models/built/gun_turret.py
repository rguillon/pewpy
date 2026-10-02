"""The player's machine-gun turret."""

from panda3d.core import NodePath, Vec3

from pewpy import config
from pewpy.graphics.models.mesh.builder import MeshBuilder


def gun_turret_model() -> NodePath:
    """The player's machine-gun turret, sitting on the ship: a dome plus a child node named "barrel" pointing down
    the screen (-Z), which the game turns toward what the turret shoots at.
    """
    size = config.MODEL_VOXEL
    dome = MeshBuilder()
    dome.ellipsoid(Vec3(0, 0, 0), Vec3(3 * size, 2 * size, 3 * size), (0.4, 0.75, 0.35, 1))
    barrel = MeshBuilder()
    barrel.box(Vec3(0, -1.5 * size, -3.5 * size), Vec3(1.2 * size, 1.2 * size, 7 * size), (0.25, 0.27, 0.3, 1))
    model = NodePath(dome.build("gun_turret"))
    model.attachNewNode(barrel.build("barrel"))
    return model
