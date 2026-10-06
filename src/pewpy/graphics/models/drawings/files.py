"""Reading the drawings' files (`data/models/<group>/<name>.json`) in any of their forms, and the parts in them."""

from dataclasses import replace
from typing import Any

from pewpy.data import data_folder, model_folder, read_model
from pewpy.graphics.models.drawings import vox
from pewpy.graphics.models.drawings.engines import Engine, parse_engines
from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.flat import parse_drawing
from pewpy.graphics.models.drawings.layered import LAYERED_KEYS, parse_layers
from pewpy.graphics.models.drawings.magica import VOX_KEYS, voxels_from_vox
from pewpy.graphics.models.drawings.voxels import OPTIONAL_DRAWING_KEYS, Voxels, voxel_cells
from pewpy.graphics.models.types import Palette

DRAWINGS_FOLDER = "models"  # data/models/<group>/<name>.json, a model each, its parts in it (see pewpy.data.read_model)


def load_drawing(name: str) -> tuple[list[str], Palette]:
    """Read `models/<group>/<name>.json` (read again every time, so edited files show up with "Reload models")."""
    data, source = read_drawing(name)
    return parse_drawing(data, source)


def load_voxels(name: str) -> Voxels:
    """Load a model's cubes from `models/<group>/<name>.json`: a flat drawing, a 3D (layered) one, or a .vox model.

    Read again every time, so edited files show up with "Reload models".
    """
    data, source = read_drawing(name)
    return parse_voxels(data, source, model_folder(name))


def load_engines(name: str) -> list[Engine]:
    """Load a model's engines."""
    data, source = read_drawing(name)
    return parse_engines(data, source)


def read_drawing(name: str) -> tuple[Any, str]:
    """Read a model's drawing, or a part's ("avalanche:a", see pewpy.data.read_model); return it and where it's from."""
    try:
        return read_model(name)
    except ValueError as error:
        raise VoxelDrawingError(str(error)) from error


def parse_voxels(data: Any, source: str = "drawing", folder: str = "") -> Voxels:  # noqa: ANN401 - decoded JSON
    """Read a model file in any of its forms (`folder`: where a .vox file it names is, within models/).

    - a flat drawing: see `parse_drawing`;
    - a 3D drawing: "layers", a list of slices from the top (nearest the camera) down, each written like a flat
      drawing's rows, and "palette" (for each character, its "color");
    - a MagicaVoxel model: "vox", the name of a .vox file next to it (MagicaVoxel's z is up, towards the camera;
      its y goes up the screen).
    Any of them can have "engines" (see `parse_engines`). A 3D drawing or a MagicaVoxel model can also have a
    "scale": how many of its cubes make one config.MODEL_VOXEL (finer models of the same size in the world; its
    engines are in its own cubes).
    """
    keys = set(data) - OPTIONAL_DRAWING_KEYS if isinstance(data, dict) else set()
    if keys == LAYERED_KEYS:
        return replace(parse_layers(data, source), scale=_scale(data, source))
    if keys == VOX_KEYS:
        if not isinstance(data["vox"], str):
            raise VoxelDrawingError.malformed(source, "'vox' must be a file name")
        path = data_folder() / DRAWINGS_FOLDER / folder / data["vox"]
        try:
            voxels = voxels_from_vox(vox.read(path.read_bytes()))
        except (OSError, vox.VoxError) as error:
            raise VoxelDrawingError.malformed(source, f"{data['vox']}: {error}") from error
        return replace(voxels, scale=_scale(data, source))
    if "scale" in data:
        raise VoxelDrawingError.malformed(source, "only 3D drawings and .vox models can have a 'scale'")
    rows, palette = parse_drawing(data, source)
    return Voxels(voxel_cells(rows, palette), len(rows[0]), len(rows))


def _scale(data: dict[str, Any], source: str) -> int:
    scale = data.get("scale", 1)
    if isinstance(scale, bool) or not isinstance(scale, int) or scale < 1:
        raise VoxelDrawingError.malformed(source, "'scale' must be a whole number, 1 or more")
    return scale
