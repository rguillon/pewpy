"""A 3D drawing: slices, the top one (nearest the camera) first."""

from typing import Any

from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.flat import palette_entry
from pewpy.graphics.models.drawings.voxels import EMPTY, Voxels
from pewpy.graphics.models.types import Color

LAYERED_KEYS = {"layers", "palette"}  # a 3D drawing: slices, the top one (nearest the camera) first


def parse_layers(data: Any, source: str) -> Voxels:
    layers = data["layers"]
    if not isinstance(layers, list) or not layers or not all(isinstance(layer, list) and layer for layer in layers):
        raise VoxelDrawingError.malformed(source, "'layers' must be a list of layers, each a list of rows")
    colors = _layer_colors(data["palette"], source)
    width, height = len(layers[0][0]), len(layers[0])
    cells = {}
    for index, layer in enumerate(layers):
        if len(layer) != height or not all(isinstance(row, str) and len(row) == width for row in layer):
            raise VoxelDrawingError.malformed(source, f"layer {index + 1}: every layer must have the same rows")
        for row_index, row in enumerate(layer):
            for column, char in enumerate(row):
                if char in EMPTY:
                    continue
                if char not in colors:
                    raise VoxelDrawingError.malformed(source, f"character {char!r} is not in the palette")
                cells[column, row_index, index - len(layers) // 2] = colors[char]  # the middle layer on the plane
    return Voxels(cells, width, height)


def _layer_colors(palette: Any, source: str) -> dict[str, Color]:
    """A 3D drawing's palette: each character's "color" (no height: the layers give the shape)."""
    if not isinstance(palette, dict):
        raise VoxelDrawingError.malformed(source, "'palette' must map characters to a color")
    colors = {}
    for char, entry in palette.items():
        if not isinstance(entry, dict) or set(entry) != {"color"}:
            raise VoxelDrawingError.malformed(source, f"palette {char!r}: expected exactly the key 'color'")
        colors[char] = palette_entry(char, {"color": entry["color"], "height": 1}, source)[0]
    return colors
