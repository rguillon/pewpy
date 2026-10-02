"""A 3D drawing from its cells."""

from pewpewdev.tools.candidates.canvas import Canvas


def layered_drawing(cells: dict[tuple[int, int, int], str], cv: Canvas, colors: dict) -> dict:
    """Make a 3D drawing: its layers from the top (nearest the camera) down, and each character's color.

    The layers are symmetric around the middle plane (the game puts the middle one on it).
    """
    extent = max(abs(layer) for _, _, layer in cells)
    layers = [
        ["".join(cells.get((x, y, layer), ".") for x in range(cv.w)) for y in range(cv.h)]
        for layer in range(-extent, extent + 1)
    ]
    used = set(cells.values())
    return {
        "layers": layers,
        "palette": {char: {"color": entry["color"]} for char, entry in colors.items() if char in used},
    }
