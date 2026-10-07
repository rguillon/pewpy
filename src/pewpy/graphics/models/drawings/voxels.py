"""A model's cubes, whatever it was drawn as."""

from dataclasses import dataclass

from pewpy import config
from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.types import Cell, Color, Palette

EMPTY = ".", " "
# weapons: read by the game (pewpy.game.enemies.mounts); parts: the drawings of the model's destructible parts, each
# named "<model>:<part>" (see pewpy.data.read_model)
OPTIONAL_DRAWING_KEYS = {"engines", "size", "weapons", "parts"}


def voxel_cells(rows: list[str], palette: Palette) -> dict[tuple[int, int, int], Color]:
    """(column, row, depth layer) -> color for every voxel of a drawing. Layer 0 is the middle of the depth."""
    if any(len(row) != len(rows[0]) for row in rows):
        raise VoxelDrawingError.ragged_rows()
    cells = {}
    for row_index, row in enumerate(rows):
        for column, char in enumerate(row):
            if char in EMPTY:
                continue
            color, thickness = palette[char]
            if thickness % 2 == 0:
                raise VoxelDrawingError.even_thickness(char)
            for layer in range(-(thickness // 2), thickness // 2 + 1):
                cells[column, row_index, layer] = color
    return cells


def thickest(palette: Palette) -> int:
    """Return how many voxels thick the thickest character of a palette is."""
    return max(height for _, height in palette.values())


@dataclass(frozen=True)
class Voxels:
    """A model's cubes, whatever it was drawn as: (column, row, layer) -> color.

    `width` columns and `height` rows (row 0 at the top of the screen), layers counted from its middle plane (negative:
    towards the camera).
    """

    cells: dict[Cell, Color]
    width: int
    height: int

    @property
    def size(self) -> float:
        """A cube's size in the world: the same on every model, config.MODEL_VOXEL."""
        return config.MODEL_VOXEL
