"""Where a model's engine flames come out."""

from dataclasses import dataclass
from typing import Any

from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.flat import palette_entry
from pewpy.graphics.models.types import Color

ENGINE_KEYS = {"x", "y", "width", "length", "towards"}
OPTIONAL_ENGINE_KEYS = {"color", "z"}
# Engine flames (see Engine): pale blue by default, a white-hot core, soft edges fading out towards the tip.
FLAME_COLOR: Color = (0.45, 0.8, 1.0, 1)
FLAME_DIRECTIONS = {"bottom": 0.0, "top": 180.0}  # roll of a flame pointing down the drawing


@dataclass(frozen=True)
class Engine:
    """Where a model's engine flame comes out, in the drawing's voxels.

    `x`, `y`: column and row of the nozzle's middle (can be between two voxels, e.g. 5.5); the flame starts at the
    edge of that voxel and goes `length` voxels towards the drawing's "top" or "bottom" (first or last row),
    `width` voxels wide at the nozzle. `z`: how many voxels above the model's middle plane (towards the camera) it
    is, for 3D models whose engines aren't on it.
    """

    x: float
    y: float
    width: float
    length: float
    towards: str
    color: Color = FLAME_COLOR
    z: float = 0.0


def parse_engines(data: Any, source: str = "drawing") -> list[Engine]:
    """A drawing's "engines": a list of {"x", "y", "width", "length", "towards", and maybe "color"} (see Engine)."""
    entries = data.get("engines", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        raise VoxelDrawingError.malformed(source, "'engines' must be a list")
    engines = []
    for index, entry in enumerate(entries):
        where = f"engine {index + 1}"
        if not isinstance(entry, dict) or not ENGINE_KEYS <= set(entry) <= ENGINE_KEYS | OPTIONAL_ENGINE_KEYS:
            keys = f"{sorted(ENGINE_KEYS)} and maybe {sorted(OPTIONAL_ENGINE_KEYS)}"
            raise VoxelDrawingError.malformed(source, f"{where}: expected the keys {keys}")
        numbers = [entry[key] for key in ("x", "y", "width", "length")]
        if not all(isinstance(value, int | float) and not isinstance(value, bool) for value in numbers):
            raise VoxelDrawingError.malformed(source, f"{where}: 'x', 'y', 'width' and 'length' must be numbers")
        if entry["width"] <= 0 or entry["length"] <= 0:
            raise VoxelDrawingError.malformed(source, f"{where}: 'width' and 'length' must be more than 0")
        if entry["towards"] not in FLAME_DIRECTIONS:
            raise VoxelDrawingError.malformed(source, f"{where}: 'towards' must be one of {sorted(FLAME_DIRECTIONS)}")
        color = FLAME_COLOR
        if "color" in entry:
            red, green, blue, _ = palette_entry("e", {"color": entry["color"], "height": 1}, source)[0]
            color = (red, green, blue, 1.0)
        z = entry.get("z", 0.0)
        if not isinstance(z, int | float) or isinstance(z, bool):
            raise VoxelDrawingError.malformed(source, f"{where}: 'z' must be a number")
        x, y, width, length = (float(value) for value in numbers)
        engines.append(Engine(x, y, width, length, entry["towards"], color, float(z)))
    return engines
