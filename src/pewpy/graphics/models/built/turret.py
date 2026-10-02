"""The turret: a base and a barrel the game turns."""

from panda3d.core import NodePath, Vec3

from pewpy import config
from pewpy.graphics.models.drawings.files import load_drawing
from pewpy.graphics.models.drawings.voxels import thickest
from pewpy.graphics.models.mesh.builder import MeshBuilder


def turret_model() -> NodePath:
    """Base plus a separate child node named "barrel" that the game turns toward the player."""
    rows, palette = load_drawing("turret")
    barrel_rows, barrel_palette = load_drawing("turret_barrel")
    size = config.MODEL_VOXEL
    base = MeshBuilder()
    base.voxels(rows, palette, size)
    barrel = MeshBuilder()
    # Starts at the center of the dome and points down the screen, just in front of the dome.
    in_front = (thickest(palette) + thickest(barrel_palette)) / 2
    barrel_center = Vec3(0, -in_front * size, -len(barrel_rows) / 2 * size)
    barrel.voxels(barrel_rows, barrel_palette, size, barrel_center)
    model = NodePath(base.build("turret"))
    model.attachNewNode(barrel.build("barrel"))
    return model
