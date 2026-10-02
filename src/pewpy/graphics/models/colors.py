"""Working with the models' colors."""

from panda3d.core import GeomNode, GeomVertexReader, NodePath

from pewpy.graphics.models.types import Cell, Color


def main_colors(model: NodePath, count: int = 3) -> tuple[Color, ...]:
    """Return the colors most of a model's vertices have (roughly: shades from ambient occlusion count as one)."""
    tally: dict[Color, int] = {}
    for path in [model, *model.findAllMatches("**/+GeomNode")]:
        node = path.node()
        if not isinstance(node, GeomNode):
            continue
        for index in range(node.getNumGeoms()):
            reader = GeomVertexReader(node.getGeom(index).getVertexData(), "color")
            while not reader.isAtEnd():
                red, green, blue, alpha = reader.getData4()
                if alpha < 1:
                    continue  # see-through parts (shield bubble) aren't debris
                key = (round(red * 10) / 10, round(green * 10) / 10, round(blue * 10) / 10, 1.0)
                tally[key] = tally.get(key, 0) + 1
    ranked = sorted(tally, key=tally.__getitem__, reverse=True)
    return tuple(ranked[:count]) or ((1.0, 1.0, 1.0, 1.0),)


def shade(color: Color, factor: float) -> Color:
    """Return a color made lighter or darker by `factor` (each channel at most 1)."""
    return (min(color[0] * factor, 1.0), min(color[1] * factor, 1.0), min(color[2] * factor, 1.0), color[3])


def tint(color: Color, by: Color) -> Color:
    """Return a color multiplied by another one, channel by channel (the alpha is `by`'s)."""
    return (color[0] * by[0], color[1] * by[1], color[2] * by[2], by[3])


METAL: Color = (0.55, 0.57, 0.62, 1)


def mottle(color: Color, cell: Cell, amount: float = 0.08) -> Color:
    """Slightly lighter or darker per voxel (always the same for a cell), so big flat areas aren't flat."""
    column, row, layer = cell
    noise = ((column * 73856093) ^ (row * 19349663) ^ (layer * 83492791)) % 1000 / 1000
    return shade(color, 1 + amount * (2 * noise - 1))
