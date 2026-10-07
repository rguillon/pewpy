"""Reading the drawings' files (`data/models/<group>/<name>.json`) in any of their forms, and the parts in them."""

from typing import Any

from pewpy.data import read_model
from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.flat import parse_drawing
from pewpy.graphics.models.drawings.layered import LAYERED_KEYS, parse_layers
from pewpy.graphics.models.drawings.voxels import OPTIONAL_DRAWING_KEYS, Voxels, voxel_cells
from pewpy.graphics.models.types import Palette

DRAWINGS_FOLDER = "models"  # data/models/<group>/<name>.json, a model each, its parts in it (see pewpy.data.read_model)


def load_drawing(name: str) -> tuple[list[str], Palette]:
    """Read `models/<group>/<name>.json`."""
    data, source = read_drawing(name)
    return parse_drawing(data, source)


def read_drawing(name: str) -> tuple[Any, str]:
    """Read a model's drawing, or a part's ("avalanche:a", see pewpy.data.read_model); return it and where it's from."""
    try:
        return read_model(name)
    except ValueError as error:
        raise VoxelDrawingError(str(error)) from error


def parse_voxels(data: Any, source: str = "drawing") -> Voxels:  # noqa: ANN401 - decoded JSON
    """Read a model file in either of its forms.

    - a flat drawing: see `parse_drawing`;
    - a 3D drawing: "layers", a list of slices from the top (nearest the camera) down, each written like a flat
      drawing's rows, and "palette" (for each character, its "color").
    Either can have "engines" (see `parse_engines`) and a "size" (see `drawing_size`). Every cube is
    config.MODEL_VOXEL, on every model.
    """
    keys = set(data) - OPTIONAL_DRAWING_KEYS if isinstance(data, dict) else set()
    if keys == LAYERED_KEYS:
        return parse_layers(data, source)
    rows, palette = parse_drawing(data, source)
    return Voxels(voxel_cells(rows, palette), len(rows[0]), len(rows))


def drawing_size(data: dict[str, Any], voxels: Voxels, source: str = "drawing") -> tuple[float, float]:
    """Return the size a model is meant to be, in world units, across and up the screen: its "size".

    New models of it are made this size (see pewpy.generators.models.sized); without one, the size its cubes cover.
    """
    if "size" not in data:
        return voxels.width * voxels.size, voxels.height * voxels.size
    size = data["size"]
    if not (
        isinstance(size, list)
        and len(size) == 2
        and all(isinstance(value, int | float) and not isinstance(value, bool) and value > 0 for value in size)
    ):
        raise VoxelDrawingError.malformed(source, "'size' must be 2 numbers more than 0")
    return float(size[0]), float(size[1])
