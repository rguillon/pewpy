"""The tank: a hull and a turret the game turns."""

from panda3d.core import NodePath, Vec3

from pewpy import config
from pewpy.graphics.models.drawings.files import load_drawing
from pewpy.graphics.models.drawings.voxels import thickest
from pewpy.graphics.models.mesh.builder import MeshBuilder


def tank_model() -> NodePath:
    """Hull plus a separate child node named "barrel" (the turret: dome and gun) that the game turns toward the
    player, around the dome's middle. The hull's treads run along the top and bottom: it drives sideways.
    """
    size = config.MODEL_VOXEL
    hull_rows, hull_palette = load_drawing("tank")
    dome_rows, dome_palette = load_drawing("tank_turret")
    barrel_rows, barrel_palette = load_drawing("tank_barrel")
    hull = MeshBuilder()
    hull.voxels(hull_rows, hull_palette, size)
    turret = MeshBuilder()
    # The dome sits on the hull (half sunk into it); the gun starts at its middle and points down the screen.
    dome_depth = -thickest(hull_palette) / 2 * size
    turret.voxels(dome_rows, dome_palette, size, Vec3(0, dome_depth, 0))
    barrel_depth = dome_depth - thickest(dome_palette) / 4 * size
    turret.voxels(barrel_rows, barrel_palette, size, Vec3(0, barrel_depth, -len(barrel_rows) / 2 * size))
    model = NodePath(hull.build("tank"))
    model.attachNewNode(turret.build("barrel"))
    return model
