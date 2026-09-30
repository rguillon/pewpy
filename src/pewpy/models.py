"""Procedural 3D models (placeholders until 05-visuals.md is decided).

Ships are voxel models, like pixel art extruded into blocks: each one is drawn as rows of characters, and a
palette gives every character a color and a thickness (in voxels, centered on the ship's depth), so the hull,
cockpit and wings stand out at different depths. The drawings are JSON files in `src/pewpy/models/` (see
`parse_drawing`); this module turns them, and the shapes that aren't drawings, into meshes.

Model space: X is right, Z is up the screen, Y is depth (negative Y faces the camera, so it is the "top"
of a ship). Every model fits in a 1 x 1 x 1 box centered on the origin and is stretched to the entity's size.
The player points up the screen (+Z); enemies point down (-Z). The first row of a drawing is the top of the screen.
"""

import itertools
import json
import math
import random
from collections.abc import Callable
from importlib import resources
from typing import Any

from panda3d.core import (
    CardMaker,
    ColorBlendAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexReader,
    GeomVertexWriter,
    NodePath,
    PNMImage,
    TextNode,
    Texture,
    TransparencyAttrib,
    Vec3,
)

Color = tuple[float, float, float, float]
Outline = list[tuple[float, float]]  # convex polygon in the X/Z plane
Palette = dict[str, tuple[Color, int]]  # character -> (color, thickness in voxels, odd)
Cell = tuple[int, int, int]  # (column, row going down the screen, depth layer going away from the camera)
UV = tuple[float, float]
Vertex = tuple[Vec3, Color, UV]
NO_BEVEL: UV = (0.5, 0.5)  # texture coordinate of shapes that aren't voxels: the shader bevels no edge
QUAD_UVS: tuple[UV, UV, UV, UV] = ((0, 0), (1, 0), (1, 1), (0, 1))
# Glowing voxel faces (lit windows, lights) have their texture coordinates moved by 2: the shader draws them as
# a bright pane, unaffected by lighting.
GLOW_UVS: tuple[UV, UV, UV, UV] = ((2, 0), (3, 0), (3, 1), (2, 1))
WATER_UV: UV = (4.5, 0.5)  # water: the shader makes waves on it
# Burning voxel faces (lava, flames) have their texture coordinates moved by 6: they shine all over, flickering.
BURN_UVS: tuple[UV, UV, UV, UV] = ((6, 0), (7, 0), (7, 1), (6, 1))

EMPTY = ".", " "
FACE_DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
# Ambient occlusion: brightness of a voxel face corner touched by 0, 1, 2 or 3 neighbor voxels in front of the face.
# Darkens inner corners and creases so the blocks read as separate cubes.
OCCLUSION_BRIGHTNESS = (1.0, 0.8, 0.66, 0.55)


class VoxelDrawingError(ValueError):
    """A voxel drawing or its palette is malformed."""

    @classmethod
    def ragged_rows(cls) -> "VoxelDrawingError":
        return cls("every row of a voxel drawing must have the same length")

    @classmethod
    def malformed(cls, source: str, message: str) -> "VoxelDrawingError":
        return cls(f"{source}: {message}")

    @classmethod
    def even_thickness(cls, char: str) -> "VoxelDrawingError":
        return cls(f"thickness of {char!r} must be odd, so the voxels stay centered")


class MeshBuilder:
    """Collects flat-shaded, colored triangles and turns them into a Panda3D GeomNode.

    Every shape is convex, so each triangle can be turned to face away from the shape's center:
    callers don't have to care about winding order.
    Voxel faces get texture coordinates from 0 to 1 across the face, which the shader (lighting.py) uses to
    bevel the edges of each cube; other shapes get `NO_BEVEL`.
    """

    def __init__(self) -> None:
        self.triangles: list[tuple[Vertex, Vertex, Vertex]] = []

    def triangle(
        self,
        a: Vec3,
        b: Vec3,
        c: Vec3,
        color: Color,
        inside: Vec3,
        brightness: tuple[float, float, float] = (1, 1, 1),
        uvs: tuple[UV, UV, UV] = (NO_BEVEL, NO_BEVEL, NO_BEVEL),
    ) -> None:
        """A flat triangle; `brightness` darkens each corner's color (the GPU blends it across the triangle)."""
        normal = (b - a).cross(c - a)
        if normal.length() < 1e-9:
            return
        va, vb, vc = (
            (corner, shade(color, light), uv) for corner, light, uv in zip((a, b, c), brightness, uvs, strict=True)
        )
        if normal.dot((a + b + c) / 3 - inside) < 0:
            vb, vc = vc, vb  # face away from the shape's center (counter-clockwise seen from outside)
        self.triangles.append((va, vb, vc))

    def quad(
        self,
        a: Vec3,
        b: Vec3,
        c: Vec3,
        d: Vec3,
        color: Color,
        inside: Vec3,
        brightness: tuple[float, float, float, float] = (1, 1, 1, 1),
        uvs: tuple[UV, UV, UV, UV] = (NO_BEVEL, NO_BEVEL, NO_BEVEL, NO_BEVEL),
    ) -> None:
        ba, bb, bc, bd = brightness
        ua, ub, uc, ud = uvs
        if ba + bc < bb + bd:
            # Split along the brighter diagonal, or the shading would show a crease across the face.
            self.triangle(a, b, d, color, inside, (ba, bb, bd), (ua, ub, ud))
            self.triangle(b, c, d, color, inside, (bb, bc, bd), (ub, uc, ud))
        else:
            self.triangle(a, b, c, color, inside, (ba, bb, bc), (ua, ub, uc))
            self.triangle(a, c, d, color, inside, (ba, bc, bd), (ua, uc, ud))

    def prism(self, outline: Outline, y_front: float, y_back: float, color: Color) -> None:
        """A flat convex outline in the X/Z plane, extruded along Y (depth) from `y_front` to `y_back`."""
        front = [Vec3(x, y_front, z) for x, z in outline]
        back = [Vec3(x, y_back, z) for x, z in outline]
        inside = sum(front + back, Vec3()) / (2 * len(outline))
        for i in range(1, len(outline) - 1):
            self.triangle(front[0], front[i], front[i + 1], color, inside)
            self.triangle(back[0], back[i], back[i + 1], color, inside)
        for i in range(len(outline)):
            j = (i + 1) % len(outline)
            self.quad(front[i], front[j], back[j], back[i], color, inside)

    def box(self, center: Vec3, size: Vec3, color: Color) -> None:
        half_x, half_z = size.x / 2, size.z / 2
        outline = [(-half_x, -half_z), (half_x, -half_z), (half_x, half_z), (-half_x, half_z)]
        moved = [(center.x + x, center.z + z) for x, z in outline]
        self.prism(moved, center.y - size.y / 2, center.y + size.y / 2, color)

    def ellipsoid(self, center: Vec3, radii: Vec3, color: Color, rings: int = 4, segments: int = 8) -> None:
        """A low-poly sphere stretched by `radii` along X, Y and Z."""

        def point(ring: int, segment: int) -> Vec3:
            latitude = math.pi * ring / rings - math.pi / 2
            longitude = 2 * math.pi * segment / segments
            return center + Vec3(
                math.cos(latitude) * math.cos(longitude) * radii.x,
                math.sin(latitude) * radii.y,
                math.cos(latitude) * math.sin(longitude) * radii.z,
            )

        for ring in range(rings):
            for segment in range(segments):
                a, b = point(ring, segment), point(ring, segment + 1)
                c, d = point(ring + 1, segment + 1), point(ring + 1, segment)
                self.quad(a, b, c, d, color, center)

    def voxels(self, rows: list[str], palette: Palette, size: float, center: Vec3 | None = None) -> None:
        """Add a voxel drawing made of cubes of `size`, the middle of the drawing at `center`.

        Faces between two touching voxels are hidden, so they are left out. Face corners next to other voxels
        are darkened (ambient occlusion).
        """
        center = center or Vec3(0, 0, 0)
        width, height = len(rows[0]), len(rows)
        origin = center + Vec3(-(width - 1) / 2 * size, 0, (height - 1) / 2 * size)
        self.cells(voxel_cells(rows, palette), size, origin)

    def cells(
        self,
        cells: dict[Cell, Color],
        size: float,
        origin: Vec3,
        context: frozenset[Cell] = frozenset(),
        glowing: frozenset[Cell] = frozenset(),
        burning: frozenset[Cell] = frozenset(),
    ) -> None:
        """Add cubes of `size`; cell (0, 0, 0) is centered on `origin`.

        `context` lists cells drawn elsewhere (e.g. the next strip of ground): they hide faces and shade corners
        like the others, but aren't drawn. Cells in `glowing` light up on their own as a pane (see GLOW_UVS), cells
        in `burning` all over (BURN_UVS).
        """
        half = size / 2
        corners = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        for (column, row, layer), color in cells.items():

            def filled(offset: Vec3, column: int = column, row: int = row, layer: int = layer) -> bool:
                cell = (column + round(offset.x), row - round(offset.z), layer + round(offset.y))
                return cell in cells or cell in context

            middle = origin + Vec3(column * size, layer * size, -row * size)
            for direction in FACE_DIRECTIONS:
                normal = Vec3(*direction)
                if filled(normal):
                    continue
                u = Vec3(0, 0, 1) if direction[0] else Vec3(1, 0, 0)  # two axes along the face
                w = normal.cross(u)
                face = middle + normal * half
                a, b, c, d = (face + (u * su + w * sw) * half for su, sw in corners)
                if (column, row, layer) in glowing:
                    self.quad(a, b, c, d, color, middle, uvs=GLOW_UVS)
                    continue
                if (column, row, layer) in burning:
                    self.quad(a, b, c, d, color, middle, uvs=BURN_UVS)
                    continue
                ba, bb, bc, bd = (occlusion(filled, normal, u * su, w * sw) for su, sw in corners)
                self.quad(a, b, c, d, color, middle, (ba, bb, bc, bd), QUAD_UVS)

    def build(self, name: str) -> GeomNode:
        data = GeomVertexData(name, GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
        data.setNumRows(len(self.triangles) * 3)
        vertex = GeomVertexWriter(data, "vertex")
        normal = GeomVertexWriter(data, "normal")
        color = GeomVertexWriter(data, "color")
        texcoord = GeomVertexWriter(data, "texcoord")
        primitive = GeomTriangles(Geom.UHStatic)
        for index, corners in enumerate(self.triangles):
            (a, _, _), (b, _, _), (c, _, _) = corners
            face_normal = (b - a).cross(c - a)
            face_normal.normalize()
            for position, rgba, uv in corners:
                vertex.addData3(position)
                normal.addData3(face_normal)
                color.addData4(*rgba)
                texcoord.addData2(*uv)
            primitive.addVertices(index * 3, index * 3 + 1, index * 3 + 2)
        geom = Geom(data)
        geom.addPrimitive(primitive)
        node = GeomNode(name)
        node.addGeom(geom)
        return node


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


def occlusion(filled: Callable[[Vec3], bool], normal: Vec3, side_a: Vec3, side_b: Vec3) -> float:
    """Brightness of one corner of a voxel face, from the voxels touching it in front of the face."""
    a, b = filled(normal + side_a), filled(normal + side_b)
    touching = 3 if a and b else a + b + filled(normal + side_a + side_b)
    return OCCLUSION_BRIGHTNESS[touching]


def voxel_size(rows: list[str], palette: Palette) -> float:
    """Size of one voxel so that the drawing fits in the unit box."""
    thickest = max(palette[char][1] for row in rows for char in row if char not in EMPTY)
    return 1 / max(len(rows[0]), len(rows), thickest)


def voxel_model(name: str, rows: list[str], palette: Palette) -> NodePath:
    mesh = MeshBuilder()
    mesh.voxels(rows, palette, voxel_size(rows, palette))
    return NodePath(mesh.build(name))


def main_colors(model: NodePath, count: int = 3) -> tuple[Color, ...]:
    """The colors most of a model's vertices have (roughly: shades from ambient occlusion count as one)."""
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
    return (min(color[0] * factor, 1.0), min(color[1] * factor, 1.0), min(color[2] * factor, 1.0), color[3])


def tint(color: Color, by: Color) -> Color:
    """A color multiplied by another one, channel by channel (the alpha is `by`'s)."""
    return (color[0] * by[0], color[1] * by[1], color[2] * by[2], by[3])


def facing_roll(dx: float, dz: float) -> float:
    """Roll angle (degrees) that turns a model pointing down the screen (-Z) to point along (dx, dz)."""
    return math.degrees(math.atan2(-dx, -dz))


METAL: Color = (0.55, 0.57, 0.62, 1)
DRAWINGS_FOLDER = "models"  # src/pewpy/models/<name>.json, one voxel drawing each
DRAWING_KEYS = {"rows", "palette"}
PALETTE_KEYS = {"color", "height"}


def make_cube(name: str = "cube") -> GeomNode:
    """A plain 1 x 1 x 1 cube centered on the origin (used for bullets)."""
    mesh = MeshBuilder()
    mesh.box(Vec3(0, 0, 0), Vec3(1, 1, 1), (1, 1, 1, 1))
    return mesh.build(name)


def load_drawing(name: str) -> tuple[list[str], Palette]:
    """Read `models/<name>.json` (read again every time, so edited files show up with "Reload models")."""
    source = f"{name}.json"
    text = (resources.files("pewpy") / DRAWINGS_FOLDER / source).read_text()
    return parse_drawing(json.loads(text), source)


def parse_drawing(data: Any, source: str = "drawing") -> tuple[list[str], Palette]:
    """A drawing file: "rows" (the drawing, one string per row, "." or " " for no voxel) and "palette" (for each
    character, its "color" as red, green, blue from 0 to 1 and its "height": how many voxels thick it is, odd)."""
    if not isinstance(data, dict) or set(data) != DRAWING_KEYS:
        raise VoxelDrawingError.malformed(source, f"expected exactly the keys {sorted(DRAWING_KEYS)}")
    rows = data["rows"]
    if not isinstance(rows, list) or not rows or not all(isinstance(row, str) for row in rows):
        raise VoxelDrawingError.malformed(source, "'rows' must be a list of strings")
    if not isinstance(data["palette"], dict):
        raise VoxelDrawingError.malformed(source, "'palette' must map characters to a color and a height")
    palette = {char: _palette_entry(char, entry, source) for char, entry in data["palette"].items()}
    unknown = {char for row in rows for char in row if char not in EMPTY} - set(palette)
    if unknown:
        raise VoxelDrawingError.malformed(source, f"characters {sorted(unknown)} are not in the palette")
    if any(len(row) != len(rows[0]) for row in rows):
        raise VoxelDrawingError.malformed(source, "every row must have the same length")
    return rows, palette


def _palette_entry(char: str, entry: Any, source: str) -> tuple[Color, int]:
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


def drawing_model(name: str) -> NodePath:
    rows, palette = load_drawing(name)
    return voxel_model(name, rows, palette)


def player_model() -> NodePath:
    return drawing_model("player")


def drone_model() -> NodePath:
    return drawing_model("drone")


def weaver_model() -> NodePath:
    return drawing_model("weaver")


def diver_model() -> NodePath:
    return drawing_model("diver")


def gunship_model() -> NodePath:
    return drawing_model("gunship")


def turret_model() -> NodePath:
    """Base plus a separate child node named "barrel" that the game turns toward the player."""
    rows, palette = load_drawing("turret")
    barrel_rows, barrel_palette = load_drawing("turret_barrel")
    size = voxel_size(rows, palette)
    base = MeshBuilder()
    base.voxels(rows, palette, size)
    barrel = MeshBuilder()
    # Starts at the center of the dome and points down the screen, in front of the dome.
    barrel_center = Vec3(0, -3 * size, -len(barrel_rows) / 2 * size)
    barrel.voxels(barrel_rows, barrel_palette, size, barrel_center)
    model = NodePath(base.build("turret"))
    model.attachNewNode(barrel.build("barrel"))
    return model


def swarmer_model() -> NodePath:
    return drawing_model("swarmer")


def sniper_model() -> NodePath:
    return drawing_model("sniper")


def mine_layer_model() -> NodePath:
    return drawing_model("mine_layer")


def mine_model() -> NodePath:
    return drawing_model("mine")


def shield_carrier_model() -> NodePath:
    return drawing_model("shield_carrier")


def shield_bubble_model() -> NodePath:
    """See-through sphere drawn around a Shield Carrier while its shield is up."""
    mesh = MeshBuilder()
    mesh.ellipsoid(Vec3(0, 0, 0), Vec3(0.62, 0.62, 0.62), (0.55, 0.85, 1.0, 0.3), rings=6, segments=12)
    bubble = NodePath(mesh.build("shield"))
    bubble.setTransparency(TransparencyAttrib.MAlpha)
    bubble.setDepthWrite(False)
    bubble.setLightOff()
    bubble.setShaderOff()
    return bubble


def splitter_model() -> NodePath:
    """Three lobes: it splits into three Swarmers."""
    return drawing_model("splitter")


def missile_model() -> NodePath:
    """Points down the screen (-Z) like the enemies, so the game can turn it with `facing_roll`."""
    return drawing_model("missile")


def pickup_model(letter: str, color: Color) -> NodePath:
    """A blocky colored capsule with a letter that always faces the camera.

    The capsule's drawing is in shades of grey, multiplied by the pickup's color."""
    rows, palette = load_drawing("capsule")
    tinted = {char: (tint(grey, color), height) for char, (grey, height) in palette.items()}
    model = voxel_model(f"pickup_{letter}", rows, tinted)
    text = TextNode("letter")
    text.setText(letter)
    text.setAlign(TextNode.ACenter)
    text.setTextColor(0.05, 0.05, 0.1, 1)
    label = model.attachNewNode(text)
    label.setScale(0.75)
    label.setPos(0, 0, -0.27)  # on the spin axis, so it stays centered while the capsule turns
    label.setBillboardPointEye()
    label.setLightOff()
    label.setShaderOff()
    # Drawn after everything else and without a depth test, so the capsule never hides it.
    label.setBin("fixed", 0)
    label.setDepthTest(False)
    label.setDepthWrite(False)
    return model


def repair_model() -> NodePath:
    return drawing_model("repair")


def laser_beam_model() -> NodePath:
    """A 1 x 1 x 1 glowing box (stretched to the beam's size): bright core inside a see-through glow."""
    mesh = MeshBuilder()
    mesh.box(Vec3(0, 0, 0), Vec3(0.4, 0.4, 1.0), (0.9, 1.0, 1.0, 1))
    mesh.box(Vec3(0, 0, 0), Vec3(1.0, 1.0, 1.0), (0.3, 0.9, 1.0, 0.45))
    beam = NodePath(mesh.build("laser"))
    beam.setTransparency(TransparencyAttrib.MAlpha)
    beam.setLightOff()
    beam.setShaderOff()
    return beam


# Backgrounds (background.py): dark and muted, so bullets and ships stay easy to see.
GROUND_COLORS: tuple[Color, ...] = (  # by height above the base layer: dusty brown, unlike the grey turrets
    (0.05, 0.045, 0.04, 1),
    (0.075, 0.065, 0.05, 1),
    (0.1, 0.085, 0.065, 1),
    (0.13, 0.11, 0.08, 1),
)
# Islands, by height above the sea (share of the highest peak): beaches, grass, forest, rock. Muted.
ISLAND_COLORS: tuple[tuple[float, Color], ...] = (
    (0.15, (0.2, 0.18, 0.12, 1)),
    (0.45, (0.07, 0.13, 0.07, 1)),
    (0.8, (0.045, 0.095, 0.05, 1)),
    (1.0, (0.13, 0.125, 0.12, 1)),
)
DEEP_WATER: Color = (0.02, 0.06, 0.1, 1)
SHALLOW_WATER_BRIGHTNESS = 2.6  # shallow water is DEEP_WATER this many times brighter (more teal-looking)
WATER_GRID = 3  # the water surface's color follows the shallows every this many voxels

# Night city: dark buildings, dim window lights (well below the bullets' brightness).
BUILDING_COLORS: tuple[Color, ...] = (
    (0.07, 0.08, 0.12, 1),
    (0.09, 0.075, 0.13, 1),
    (0.06, 0.09, 0.11, 1),
    (0.1, 0.1, 0.12, 1),
)
STREET_COLOR: Color = (0.03, 0.032, 0.045, 1)
PLAZA_COLOR: Color = (0.05, 0.055, 0.07, 1)
WINDOW_COLORS: tuple[Color, ...] = ((0.12, 0.42, 0.46, 1), (0.5, 0.32, 0.12, 1))  # teal, amber
STREET_LIGHT_COLOR: Color = (0.08, 0.32, 0.4, 1)  # dim cyan: nothing pink, like the enemy bullets
BEACON_COLOR: Color = (0.45, 0.06, 0.05, 1)
ROCK_COLORS: tuple[Color, ...] = ((0.16, 0.15, 0.15, 1), (0.2, 0.18, 0.16, 1), (0.13, 0.13, 0.15, 1))
PLANET_COLORS: tuple[Color, ...] = ((0.12, 0.13, 0.25, 1), (0.16, 0.14, 0.28, 1), (0.1, 0.16, 0.24, 1))


def mottle(color: Color, cell: Cell, amount: float = 0.08) -> Color:
    """Slightly lighter or darker per voxel (always the same for a cell), so big flat areas aren't flat."""
    column, row, layer = cell
    noise = ((column * 73856093) ^ (row * 19349663) ^ (layer * 83492791)) % 1000 / 1000
    return shade(color, 1 + amount * (2 * noise - 1))


def ground_cells(heights: list[list[int]], first_row: int = 0, max_height: int = 3) -> dict[Cell, Color]:
    """A voxel column per height: the base layer plus `height` voxels rising towards the camera (layer < 0).

    The color depends on the column's height, as a share of `max_height`.
    """
    cells = {}
    for row, line in enumerate(heights):
        for column, height in enumerate(line):
            color = GROUND_COLORS[min(height * len(GROUND_COLORS) // (max_height + 1), len(GROUND_COLORS) - 1)]
            for level in range(height + 1):
                cell = (column, first_row + row, -level)
                cells[cell] = mottle(color, cell)
    return cells


def city_cells(
    heights: list[list[int]], lots: list[list[int]], max_height: int
) -> tuple[dict[Cell, Color], frozenset[Cell]]:
    """A night city: (cells, glowing cells). Buildings have floors of wall and rows of windows, some lit;
    roofs are a bit lighter with small blocks (machinery) on them, the tallest towers have one red beacon at a
    corner; streets (lot 0) have a few lights."""
    cells: dict[Cell, Color] = {}
    glowing: set[Cell] = set()
    for row, (line, line_lots) in enumerate(zip(heights, lots, strict=True)):
        for column, (height, lot) in enumerate(zip(line, line_lots, strict=True)):
            if lot == 0 or height == 0:
                _street(cells, glowing, (column, row, 0), plaza=lot != 0)
            else:
                corner = (column == 0 or line_lots[column - 1] != lot) and (row == 0 or lots[row - 1][column] != lot)
                beacon = corner and height >= 0.7 * max_height
                _building_column(cells, glowing, (column, row), height, lot, beacon)
    return cells, frozenset(glowing)


def _street(cells: dict[Cell, Color], glowing: set[Cell], cell: Cell, plaza: bool) -> None:
    column, row, _ = cell
    if _noise(column, row, 1) < 0.05:
        cells[cell] = STREET_LIGHT_COLOR
        glowing.add(cell)
    else:
        cells[cell] = mottle(PLAZA_COLOR if plaza else STREET_COLOR, cell)


def _building_column(
    cells: dict[Cell, Color], glowing: set[Cell], place: tuple[int, int], height: int, lot: int, beacon: bool
) -> None:
    column, row = place
    base = BUILDING_COLORS[lot % len(BUILDING_COLORS)]
    lit_share = 0.08 + 0.35 * _noise(lot, 0, 3)  # some buildings are busier than others
    window = WINDOW_COLORS[lot % len(WINDOW_COLORS)]
    for level in range(height):
        cell = (column, row, -level)
        if level % 2 == 0:  # floor slab
            cells[cell] = mottle(base, cell)
        elif _noise(column, row, level) < lit_share:  # a row of windows: lit...
            cells[cell] = window
            glowing.add(cell)
        else:  # ...or dark glass
            cells[cell] = shade(base, 0.55)
    roof = (column, row, -height)
    if beacon:
        cells[roof] = BEACON_COLOR
        glowing.add(roof)
        return
    cells[roof] = mottle(shade(base, 1.2), roof)
    if _noise(column, row, 4) < 0.07:  # rooftop machinery
        machinery = (column, row, -height - 1)
        cells[machinery] = mottle(shade(base, 0.9), machinery)


def island_cells(heights: list[list[int]], max_height: int) -> dict[Cell, Color]:
    """Land voxels (height 0 is water: no voxel), colored by their own height, so slopes show bands."""
    cells = {}
    for row, line in enumerate(heights):
        for column, height in enumerate(line):
            for level in range(1, height + 1):
                share = level / max(max_height, 1)
                color = next(color for limit, color in ISLAND_COLORS if share <= limit)
                cell = (column, row, -level)
                cells[cell] = mottle(color, cell, 0.12)
    return cells


def water_surface(
    mesh: MeshBuilder, shallows: list[list[float]], voxel: float, columns: int, deep: Color = DEEP_WATER
) -> None:
    """The sea as a flat surface just below the first land voxels, lighter where `shallows` is high.

    `shallows` has one more row than the strip (its bottom edge). A coarse grid: the colors blend in between.
    """
    rows = len(shallows) - 1
    xs = [*range(0, columns, WATER_GRID), columns]
    zs = [*range(0, rows, WATER_GRID), rows]

    def corner(column: int, row: int) -> tuple[Vec3, float]:
        shallow = shallows[row][min(column, columns - 1)]
        # At the bottom of the first land voxels (level 1, centered one voxel in front of the base layer).
        return Vec3(column * voxel, -voxel / 2, -row * voxel), 1 + (SHALLOW_WATER_BRIGHTNESS - 1) * shallow

    for top, bottom in itertools.pairwise(zs):
        for left, right in itertools.pairwise(xs):
            (a, ba), (b, bb) = corner(left, bottom), corner(right, bottom)
            (c, bc), (d, bd) = corner(right, top), corner(left, top)
            behind = (a + c) / 2 + Vec3(0, 1, 0)  # the surface faces the camera (-Y)
            mesh.quad(a, b, c, d, deep, behind, (ba, bb, bc, bd), (WATER_UV, WATER_UV, WATER_UV, WATER_UV))


def _noise(a: int, b: int, c: int) -> float:
    """A number in [0, 1), always the same for the same arguments."""
    return ((a * 73856093) ^ (b * 19349663) ^ (c * 83492791)) % 10007 / 10007


def buried(cell: Cell, solid: frozenset[Cell]) -> bool:
    column, row, layer = cell
    return all((column + dx, row - dz, layer + dy) in solid for dx, dy, dz in FACE_DIRECTIONS)


def rock_model(shape: int) -> NodePath:
    """A lumpy voxel asteroid, the same for the same `shape`; fits the unit box."""
    rng = random.Random(shape)  # noqa: S311 - visual randomness, not cryptography
    radius = 3
    stretch = Vec3(rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.0))
    cells = {}
    for column in range(-radius, radius + 1):
        for row in range(-radius, radius + 1):
            for layer in range(-radius, radius + 1):
                distance = Vec3(column / stretch.x, row / stretch.z, layer / stretch.y).length()
                if distance <= radius + rng.uniform(-0.6, 0.4):
                    cell = (column, row, layer)
                    cells[cell] = mottle(rng.choice(ROCK_COLORS), cell, 0.15)
    mesh = MeshBuilder()
    mesh.cells(cells, 1 / (2 * radius + 1), Vec3(0, 0, 0))
    return NodePath(mesh.build(f"rock_{shape}"))


def distant_planet_model(colors: tuple[Color, ...] = PLANET_COLORS, seed: int = 7) -> NodePath:
    """A big voxel planet with muted bands of `colors`; fits the unit box."""
    radius = 9
    rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
    band_colors = [rng.choice(colors) for _ in range(2 * radius + 1)]
    cells = {}
    for column in range(-radius, radius + 1):
        for row in range(-radius, radius + 1):
            for layer in range(-radius, radius + 1):
                if column * column + row * row + layer * layer <= radius * radius + radius:
                    cell = (column, row, layer)
                    cells[cell] = mottle(band_colors[row + radius], cell, 0.12)
    mesh = MeshBuilder()
    mesh.cells(cells, 1 / (2 * radius + 1), Vec3(0, 0, 0))
    return NodePath(mesh.build("distant_planet"))


def cloud_model(color: Color, seed: int = 0) -> NodePath:
    """A soft, lumpy glow on a 1 x 1 card, added to what's behind it (unlit, see-through)."""
    size = 64
    rng = random.Random(seed)  # noqa: S311 - visual randomness, not cryptography
    blobs = [(rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7), rng.uniform(0.12, 0.25)) for _ in range(5)]
    image = PNMImage(size, size)
    for y in range(size):
        for x in range(size):
            u, v = (x + 0.5) / size, (y + 0.5) / size
            glow = sum(math.exp(-((u - bx) ** 2 + (v - by) ** 2) / (2 * r * r)) for bx, by, r in blobs) / 2.5
            edge = max(0.0, 1 - 2 * math.hypot(u - 0.5, v - 0.5)) ** 0.5  # nothing at the card's edges
            value = min(glow * edge, 1.0)
            image.setXel(x, y, color[0] * value, color[1] * value, color[2] * value)
    texture = Texture("cloud")
    texture.load(image)
    card = CardMaker("cloud")
    card.setFrame(-0.5, 0.5, -0.5, 0.5)
    cloud = NodePath(card.generate())
    cloud.setTexture(texture)
    cloud.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
    cloud.setDepthWrite(False)
    cloud.setLightOff()
    cloud.setShaderOff()
    return cloud


MIST_TEXTURES = 4  # different cloud shapes, built once and shared
_mist_textures: dict[int, Texture] = {}


def mist_model(shape: int) -> NodePath:
    """A soft, lumpy, see-through cloud on a 1 x 1 card, white: color it with setColor (alpha: how see-through)."""
    shape %= MIST_TEXTURES
    if shape not in _mist_textures:
        size = 64
        rng = random.Random(100 + shape)  # noqa: S311 - visual randomness, not cryptography
        blobs = [(rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7), rng.uniform(0.1, 0.22)) for _ in range(7)]
        image = PNMImage(size, size, 4)
        for y in range(size):
            for x in range(size):
                u, v = (x + 0.5) / size, (y + 0.5) / size
                puff = sum(math.exp(-((u - bx) ** 2 + (v - by) ** 2) / (2 * r * r)) for bx, by, r in blobs) / 2.2
                edge = max(0.0, 1 - 2 * math.hypot(u - 0.5, v - 0.5)) ** 0.6  # nothing at the card's edges
                image.setXelA(x, y, 1.0, 1.0, 1.0, min(puff * edge, 1.0))
        texture = Texture(f"mist_{shape}")
        texture.load(image)
        _mist_textures[shape] = texture
    card = CardMaker("mist")
    card.setFrame(-0.5, 0.5, -0.5, 0.5)
    mist = NodePath(card.generate())
    mist.setTexture(_mist_textures[shape])
    mist.setTransparency(TransparencyAttrib.MAlpha)
    mist.setDepthWrite(False)
    mist.setTwoSided(True)
    mist.setLightOff()
    mist.setShaderOff()
    return mist
