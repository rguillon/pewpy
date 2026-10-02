"""A flat drawing: rows of characters, each color given a thickness."""

from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.voxels import EMPTY, OPTIONAL_DRAWING_KEYS
from pewpy.graphics.models.types import Color, Palette

DRAWING_KEYS = {"rows", "palette"}  # a flat drawing, each color given a thickness
PALETTE_KEYS = {"color", "height"}


def parse_drawing(data: object, source: str = "drawing") -> tuple[list[str], Palette]:
    """Read a drawing file: "rows" and "palette".

    "rows": the drawing, one string per row, "." or " " for no voxel. "palette": for each character, its "color" as red,
    green, blue from 0 to 1 and its "height": how many voxels thick it is, odd. It can also have "engines" (see
    `parse_engines`).
    """
    if not isinstance(data, dict) or not DRAWING_KEYS <= set(data) <= DRAWING_KEYS | OPTIONAL_DRAWING_KEYS:
        keys = f"{sorted(DRAWING_KEYS)} and maybe {sorted(OPTIONAL_DRAWING_KEYS)}"
        raise VoxelDrawingError.malformed(source, f"expected the keys {keys}")
    rows = data["rows"]
    if not isinstance(rows, list) or not rows or not all(isinstance(row, str) for row in rows):
        raise VoxelDrawingError.malformed(source, "'rows' must be a list of strings")
    if not isinstance(data["palette"], dict):
        raise VoxelDrawingError.malformed(source, "'palette' must map characters to a color and a height")
    palette = {char: palette_entry(char, entry, source) for char, entry in data["palette"].items()}
    unknown = {char for row in rows for char in row if char not in EMPTY} - set(palette)
    if unknown:
        raise VoxelDrawingError.malformed(source, f"characters {sorted(unknown)} are not in the palette")
    if any(len(row) != len(rows[0]) for row in rows):
        raise VoxelDrawingError.malformed(source, "every row must have the same length")
    return rows, palette


def palette_entry(char: str, entry: object, source: str) -> tuple[Color, int]:
    """Read a palette entry: the character's color and height."""
    where = f"palette {char!r}"
    if len(char) != 1 or char in EMPTY:
        raise VoxelDrawingError.malformed(source, f"{where}: must be one character, not '.' or ' '")
    if not isinstance(entry, dict) or set(entry) != PALETTE_KEYS:
        raise VoxelDrawingError.malformed(source, f"{where}: expected exactly the keys {sorted(PALETTE_KEYS)}")
    color, height = entry["color"], entry["height"]
    if not (
        isinstance(color, list) and len(color) == 3 and all(isinstance(v, int | float) and 0 <= v <= 1 for v in color)
    ):
        raise VoxelDrawingError.malformed(source, f"{where}: 'color' must be 3 numbers from 0 to 1")
    if not isinstance(height, int) or isinstance(height, bool) or height < 1 or height % 2 == 0:
        raise VoxelDrawingError.malformed(source, f"{where}: 'height' must be an odd whole number, 1 or more")
    return (float(color[0]), float(color[1]), float(color[2]), 1.0), height
