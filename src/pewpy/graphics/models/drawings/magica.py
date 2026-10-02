"""A MagicaVoxel model (.vox) next to the drawing's file, and back."""

from pewpy.graphics.models.drawings import vox
from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.voxels import Voxels

VOX_KEYS = {"vox"}  # a MagicaVoxel model next to the file


def voxels_from_vox(model: vox.VoxModel) -> Voxels:
    """Read a MagicaVoxel model lying on the ground, seen from above.

    Its x goes across, its y up the screen, its z up towards the camera.
    """
    size_x, size_y, size_z = model.size
    cells = {}
    for x, y, z, index in model.voxels:
        red, green, blue, _ = model.palette[index - 1]
        cells[x, size_y - 1 - y, size_z // 2 - z] = (red / 255, green / 255, blue / 255, 1.0)
    return Voxels(cells, size_x, size_y)


def voxels_to_vox(voxels: Voxels) -> vox.VoxModel:
    """Write the cubes as a MagicaVoxel model (for editing it there): the same colors (up to 255 of them)."""
    layers = [layer for _, _, layer in voxels.cells] or [0]
    size_z = 2 * max(abs(min(layers)), abs(max(layers))) + 1
    palette: dict[tuple[int, int, int, int], int] = {}
    points = []
    for (column, row, layer), color in voxels.cells.items():
        rgba = (round(color[0] * 255), round(color[1] * 255), round(color[2] * 255), 255)
        index = palette.setdefault(rgba, len(palette) + 1)
        if index > 255:
            raise VoxelDrawingError.malformed("vox", "more than 255 colors")  # noqa: EM101 - the error builds its message
        points.append((column, voxels.height - 1 - row, size_z // 2 - layer, index))
    return vox.VoxModel((voxels.width, voxels.height, size_z), points, list(palette))
