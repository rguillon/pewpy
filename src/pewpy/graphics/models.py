"""Procedural 3D models (placeholders until 05-visuals.md is decided).

Ships are voxel models, like pixel art extruded into blocks: each one is drawn as rows of characters, and a
palette gives every character a color and a thickness (in voxels, centered on the ship's depth), so the hull,
cockpit and wings stand out at different depths. The drawings are JSON files in `src/pewpy/models/` (see
`parse_drawing`); this module turns them, and the shapes that aren't drawings, into meshes.

Model space: X is right, Z is up the screen, Y is depth (negative Y faces the camera, so it is the "top"
of a ship). Drawn models are in world units: every cube is config.MODEL_VOXEL (the same on every ship), the
middle of the drawing at the origin. Other shapes (shield bubble, laser, cube) fit in a 1 x 1 x 1 box and are
stretched to their size.
The player points up the screen (+Z); enemies point down (-Z). The first row of a drawing is the top of the screen.
"""

import json
import math
import random
from dataclasses import dataclass, replace
from typing import Any

import numpy as np
from numpy.typing import NDArray
from panda3d.core import (
    CardMaker,
    ColorBlendAttrib,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexReader,
    NodePath,
    PandaNode,
    PNMImage,
    TextNode,
    Texture,
    TransparencyAttrib,
    Vec3,
)

from pewpy import config
from pewpy.data import data_folder
from pewpy.graphics import vox

Color = tuple[float, float, float, float]
Outline = list[tuple[float, float]]  # convex polygon in the X/Z plane
Palette = dict[str, tuple[Color, int]]  # character -> (color, thickness in voxels, odd)
Cell = tuple[int, int, int]  # (column, row going down the screen, depth layer going away from the camera)
UV = tuple[float, float]
Vertex = tuple[Vec3, Color, UV]
Direction = tuple[int, int, int]
FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
BoolArray = NDArray[np.bool_]
NO_BEVEL: UV = (0.5, 0.5)  # texture coordinate of shapes that aren't voxels: the shader bevels no edge
# Voxel faces: texture coordinates count cubes from 0 across the face (a merged face covers several cubes, see
# MeshBuilder.cells), and the shader bevels every cube. One cube's face:
QUAD_UVS: tuple[UV, UV, UV, UV] = ((0, 0), (1, 0), (1, 1), (0, 1))
# Other kinds of faces have negative texture coordinates, one cube each.
# Glowing voxel faces (lit windows, lights): the shader draws them as a bright pane, unaffected by lighting.
GLOW_UVS: tuple[UV, UV, UV, UV] = ((-2, 0), (-1, 0), (-1, 1), (-2, 1))
WATER_UV: UV = (-3.5, 0.5)  # water: the shader makes waves on it
# Burning voxel faces (lava, flames): they shine all over, flickering.
BURN_UVS: tuple[UV, UV, UV, UV] = ((-6, 0), (-5, 0), (-5, 1), (-6, 1))

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
    Voxel faces get texture coordinates counting cubes across the face, which the shader (lighting.py) uses to
    bevel the edges of each cube; other shapes get `NO_BEVEL`.

    Shapes made a triangle at a time (boxes, spheres, water) are kept as Python tuples. Voxels (`cells`), which make
    up nearly every model and ground, are worked out in bulk with numpy and kept as arrays.
    """

    def __init__(self) -> None:
        self._triangles: list[tuple[Vertex, Vertex, Vertex]] = []
        # Voxel triangles, a block per `cells` call: corner positions (n, 3, 3), normals (n, 3), corner colors
        # (n, 3, 4) and corner texture coordinates (n, 3, 2).
        self._blocks: list[tuple[FloatArray, FloatArray, FloatArray, FloatArray]] = []

    @property
    def triangles(self) -> list[tuple[Vertex, Vertex, Vertex]]:
        """Every triangle so far, as (position, color, texture coordinate) corners."""
        result = list(self._triangles)
        for positions, _, colors, uvs in self._blocks:
            for corners, rgbas, coordinates in zip(positions.tolist(), colors.tolist(), uvs.tolist(), strict=True):
                a, b, c = [
                    (Vec3(x, y, z), (red, green, blue, alpha), (s, t))
                    for (x, y, z), (red, green, blue, alpha), (s, t) in zip(corners, rgbas, coordinates, strict=True)
                ]
                result.append((a, b, c))
        return result

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
        va, vb, vc = [
            (corner, shade(color, light), uv) for corner, light, uv in zip((a, b, c), brightness, uvs, strict=True)
        ]
        if normal.dot((a + b + c) / 3 - inside) < 0:
            vb, vc = vc, vb  # face away from the shape's center (counter-clockwise seen from outside)
        self._triangles.append((va, vb, vc))

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

    def drawn_cells(self, voxels: "Voxels", size: float, center: Vec3 | None = None) -> None:
        """Add a model's cubes (of `size`), the middle of its drawing at `center`."""
        center = center or Vec3(0, 0, 0)
        origin = center + Vec3(-(voxels.width - 1) / 2 * size, 0, (voxels.height - 1) / 2 * size)
        self.cells(voxels.cells, size, origin)

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

        Works on every cube at once (numpy): which faces show, how dark their corners are, then faces that look
        alike are merged into rectangles (fewer triangles, same look, see `merged_faces`).
        """
        if not cells:
            return
        # Positions in cubes along the model's X (column), Y (depth layer) and Z (up: minus the row).
        positions = _model_axes(np.array(list(cells), dtype=np.int64))
        color_indices: dict[Color, int] = {}
        color_of = np.array([color_indices.setdefault(color, len(color_indices)) for color in cells.values()])
        colors = np.array(list(color_indices), dtype=np.float64)
        special = np.zeros(len(positions), dtype=np.int64)  # 0: plain voxel, 1: glowing, 2: burning
        if glowing or burning:
            special = np.array([2 if cell in burning else 1 if cell in glowing else 0 for cell in cells])
        occupancy = _Occupancy(positions, _model_axes(np.array(list(context), dtype=np.int64).reshape(-1, 3)))
        origin_array = np.array(origin, dtype=np.float64)
        for direction in FACE_DIRECTIONS:
            normal, u, w = _FACE_AXES[direction]
            shown = ~occupancy.filled(positions + normal)
            face_positions, face_colors, face_special = positions[shown], color_of[shown], special[shown]
            for kind, uvs in ((1, GLOW_UVS), (2, BURN_UVS)):
                picked = face_special == kind
                if picked.any():
                    self._single_faces(
                        face_positions[picked], colors[face_colors[picked]], uvs, direction, size, origin_array
                    )
            plain = face_special == 0
            face_positions, face_colors = face_positions[plain], face_colors[plain]
            if not len(face_positions):
                continue
            ahead = face_positions + normal  # the cells just in front of each face
            levels = np.stack(
                [
                    occlusion_level(
                        occupancy.filled(ahead + u * su),
                        occupancy.filled(ahead + w * sw),
                        occupancy.filled(ahead + u * su + w * sw),
                    )
                    for su, sw in FACE_CORNERS
                ],
                axis=1,
            )
            rectangles = merged_faces(
                face_positions @ normal, face_positions @ u, face_positions @ w, face_colors, levels
            )
            self._rectangles(rectangles, colors, direction, size, origin_array)

    def _rectangles(
        self, rectangles: IntArray, colors: FloatArray, direction: Direction, size: float, origin: FloatArray
    ) -> None:
        """Add the rectangles from `merged_faces` lying in the planes facing `direction`."""
        normal, u, w = _FACE_AXES[direction]
        depth, along_u, along_w, width, height, color, levels = (
            rectangles[:, 0],
            rectangles[:, 1],
            rectangles[:, 2],
            rectangles[:, 3],
            rectangles[:, 4],
            rectangles[:, 5],
            rectangles[:, 6:10],
        )
        # The middle of each rectangle's first cube, then the corner of its face, then the face's 4 corners taken
        # along u then w: since u x w is the normal, they wind counter-clockwise seen from outside.
        first = origin + (np.outer(along_u, u) + np.outer(along_w, w) + np.outer(depth, normal)) * size
        corner = first + (normal - u - w) * (size / 2)
        span_u, span_w = np.outer(width * size, u), np.outer(height * size, w)
        corners = np.stack([corner, corner + span_u, corner + span_u + span_w, corner + span_w], axis=1)
        uvs = np.zeros((len(rectangles), 4, 2))  # counting cubes: (0, 0), (width, 0), (width, height), (0, height)
        uvs[:, 1:3, 0] = width[:, None]
        uvs[:, 2:4, 1] = height[:, None]
        self._faces(corners, colors[color], np.array(OCCLUSION_BRIGHTNESS)[levels], uvs, normal)

    def _single_faces(
        self,
        positions: IntArray,
        colors: FloatArray,
        uvs: tuple[UV, UV, UV, UV],
        direction: Direction,
        size: float,
        origin: FloatArray,
    ) -> None:
        """A face per cube, not merged nor shaded (glowing and burning faces: the shader draws each as a pane)."""
        normal, u, w = _FACE_AXES[direction]
        face = origin + positions * size + normal * (size / 2)
        corners = np.stack([face + (u * su + w * sw) * (size / 2) for su, sw in FACE_CORNERS], axis=1)
        count = len(positions)
        corner_uvs = np.broadcast_to(np.array(uvs, dtype=np.float64), (count, 4, 2))
        self._faces(corners, colors, np.ones((count, 4)), corner_uvs, normal)

    def _faces(
        self, corners: FloatArray, colors: FloatArray, brightness: FloatArray, uvs: FloatArray, normal: IntArray
    ) -> None:
        """Faces from their 4 corners (winding counter-clockwise seen from outside), each split in two triangles
        along the brighter diagonal, or the shading would show a crease across the face (like `quad`).
        """
        crease = brightness[:, 0] + brightness[:, 2] < brightness[:, 1] + brightness[:, 3]
        # Which corners make each face's two triangles: (a, b, d) and (b, c, d), or (a, b, c) and (a, c, d).
        picks = np.where(crease[:, None, None], [[0, 1, 3], [1, 2, 3]], [[0, 1, 2], [0, 2, 3]]).reshape(-1, 3)
        faces = np.repeat(np.arange(len(corners)), 2)  # the face of each triangle
        base = colors[faces]
        rgb = np.minimum(base[:, None, :3] * brightness[faces[:, None], picks][..., None], 1.0)  # like `shade`
        alpha = np.broadcast_to(base[:, None, 3:], (len(picks), 3, 1))
        normals = np.broadcast_to(normal.astype(np.float64), (len(picks), 3))
        self._blocks.append((
            corners[faces[:, None], picks],
            normals,
            np.concatenate([rgb, alpha], axis=2),
            uvs[faces[:, None], picks],
        ))

    def build(self, name: str) -> GeomNode:
        positions, normals, colors, uvs = self._arrays()
        count = len(positions) * 3
        vertices = np.empty(count, dtype=VERTEX_DTYPE)
        vertices["position"] = positions.reshape(-1, 3)
        vertices["normal"] = np.repeat(normals, 3, axis=0)
        # Colors are stored as bytes; Panda3D converts a float the same way (in 32 bits, rounding down).
        vertices["color"] = np.clip(np.floor(colors.reshape(-1, 4).astype(np.float32) * np.float32(255)), 0, 255)
        vertices["uv"] = uvs.reshape(-1, 2)
        data = GeomVertexData(name, GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
        data.uncleanSetNumRows(count)
        primitive = GeomTriangles(Geom.UHStatic)
        if count:
            data.modifyArrayHandle(0).copyDataFrom(vertices.view(np.uint8))
            primitive.addConsecutiveVertices(0, count)
        geom = Geom(data)
        geom.addPrimitive(primitive)
        node = GeomNode(name)
        node.addGeom(geom)
        return node

    def _arrays(self) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray]:
        """Every triangle as arrays: corner positions (n, 3, 3), normals (n, 3), colors (n, 3, 4), uvs (n, 3, 2)."""
        blocks = list(self._blocks)
        if self._triangles:
            positions = np.array([[tuple(corner) for corner, _, _ in triangle] for triangle in self._triangles])
            normals = np.cross(positions[:, 1] - positions[:, 0], positions[:, 2] - positions[:, 0])
            normals /= np.linalg.norm(normals, axis=1, keepdims=True)
            colors = np.array([[color for _, color, _ in triangle] for triangle in self._triangles], dtype=np.float64)
            uvs = np.array([[uv for _, _, uv in triangle] for triangle in self._triangles], dtype=np.float64)
            blocks.insert(0, (positions, normals, colors, uvs))
        if not blocks:
            return np.zeros((0, 3, 3)), np.zeros((0, 3)), np.zeros((0, 3, 4)), np.zeros((0, 3, 2))
        positions, normals, colors, uvs = (np.concatenate([block[part] for block in blocks]) for part in range(4))
        return positions, normals, colors, uvs


# One vertex as the GPU gets it: GeomVertexFormat.getV3n3c4t2(), a single interleaved array of 36 bytes.
VERTEX_DTYPE = np.dtype([("position", "<f4", 3), ("normal", "<f4", 3), ("color", "u1", 4), ("uv", "<f4", 2)])
# The 4 corners of a voxel face, as steps along its two axes (u, w), in winding order.
FACE_CORNERS = ((-1, -1), (1, -1), (1, 1), (-1, 1))


def face_axes(direction: Direction) -> tuple[IntArray, IntArray, IntArray]:
    """The normal of a voxel face looking along `direction` and two axes along the face (u, w), in cubes: u x w is
    the normal, so corners taken along u then w wind counter-clockwise seen from outside.
    """
    normal = np.array(direction, dtype=np.int64)
    u = np.array((0, 0, 1) if direction[0] else (1, 0, 0), dtype=np.int64)
    return normal, u, np.cross(normal, u)


_FACE_AXES = {direction: face_axes(direction) for direction in FACE_DIRECTIONS}


def _model_axes(cells: IntArray) -> IntArray:
    """Cells (column, row, layer) as positions in cubes along the model's X, Y (depth) and Z (up the screen)."""
    return np.stack([cells[:, 0], cells[:, 2], -cells[:, 1]], axis=1) if len(cells) else np.zeros((0, 3), np.int64)


class _Occupancy:
    """Which cube positions hold a voxel (drawn or context), as a 3D grid: one lookup for many positions at once."""

    def __init__(self, drawn: IntArray, context: IntArray) -> None:
        everything = np.concatenate([drawn, context])
        self.low = everything.min(axis=0) - 1  # neighbors are at most one cube away along each axis
        self.grid = np.zeros(everything.max(axis=0) - self.low + 2, dtype=bool)
        self.grid[tuple((everything - self.low).T)] = True

    def filled(self, positions: IntArray) -> BoolArray:
        return self.grid[tuple((positions - self.low).T)]


def occlusion_level(side_a: BoolArray, side_b: BoolArray, corner: BoolArray) -> IntArray:
    """How many voxels touch voxel face corners (0 to 3), from the cells in front of each face along its two edges
    (`side_a`, `side_b`) and diagonally (`corner`). With both sides filled the corner is fully tucked in (3),
    whatever the diagonal. OCCLUSION_BRIGHTNESS gives the brightness of each level.
    """
    return np.where(side_a & side_b, 3, side_a.astype(np.int64) + side_b + corner)


def merged_faces(depth: IntArray, along_u: IntArray, along_w: IntArray, colors: IntArray, levels: IntArray) -> IntArray:
    """Cover faces facing the same way with as few rectangles as possible (greedy meshing), each made of faces with
    the same color and corner shading.

    Faces are given by their plane (`depth`), place in it (`along_u`, `along_w`, in cubes), color index and corner
    occlusion levels (n, 4). A rectangle grows along u, then w, from its first face in (depth, u, w) order, and
    only along a direction where its shading doesn't change, so the GPU blends it the same as the faces it replaces.
    Returns rows of (depth, u, w, width, height, color, 4 corner levels).
    """
    keys = colors * 256 + levels[:, 0] * 64 + levels[:, 1] * 16 + levels[:, 2] * 4 + levels[:, 3]
    left = dict(zip(zip(depth.tolist(), along_u.tolist(), along_w.tolist(), strict=True), keys.tolist(), strict=True))
    rectangles = []
    for d, a, b in sorted(left):
        key = left.get((d, a, b))
        if key is None:
            continue  # already in a rectangle
        ba, bb, bc, bd = (key >> 6) & 3, (key >> 4) & 3, (key >> 2) & 3, key & 3
        width = 1
        if ba == bb and bd == bc:  # the same shading at both ends along u
            while left.get((d, a + width, b)) == key:
                width += 1
        height = 1
        if ba == bd and bb == bc:  # the same along w
            while all(left.get((d, a + i, b + height)) == key for i in range(width)):
                height += 1
        for i in range(width):
            for j in range(height):
                del left[d, a + i, b + j]
        rectangles.append((d, a, b, width, height, key >> 8, ba, bb, bc, bd))
    return np.array(rectangles, dtype=np.int64).reshape(-1, 10)


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
    return max(height for _, height in palette.values())


def voxel_model(name: str, rows: list[str], palette: Palette) -> NodePath:
    """A drawing's model, in world units: every cube is config.MODEL_VOXEL, the middle of the drawing at the origin."""
    mesh = MeshBuilder()
    mesh.voxels(rows, palette, config.MODEL_VOXEL)
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
DRAWING_KEYS = {"rows", "palette"}  # a flat drawing, each color given a thickness
LAYERED_KEYS = {"layers", "palette"}  # a 3D drawing: slices, the top one (nearest the camera) first
VOX_KEYS = {"vox"}  # a MagicaVoxel model next to the file
OPTIONAL_DRAWING_KEYS = {"engines", "scale"}
PALETTE_KEYS = {"color", "height"}
ENGINE_KEYS = {"x", "y", "width", "length", "towards"}
OPTIONAL_ENGINE_KEYS = {"color", "z"}
# Engine flames (see Engine): pale blue by default, a white-hot core, soft edges fading out towards the tip.
FLAME_COLOR: Color = (0.45, 0.8, 1.0, 1)
FLAME_CORE_COLOR: Color = (0.95, 0.98, 1.0, 1)
FLAME_CORE_SIZE = (0.45, 0.5)  # the core's width and length, as a part of the flame's
FLAME_TEXTURE_SIZE = (32, 64)
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


@dataclass(frozen=True)
class Voxels:
    """A model's cubes, whatever it was drawn as: (column, row, layer) -> color, `width` columns and `height` rows
    (row 0 at the top of the screen), layers counted from its middle plane (negative: towards the camera).
    """

    cells: dict[Cell, Color]
    width: int
    height: int
    scale: int = 1  # cubes per config.MODEL_VOXEL: a finer model, the same size in the world

    @property
    def size(self) -> float:
        """A cube's size in the world."""
        return config.MODEL_VOXEL / self.scale


def make_cube(name: str = "cube") -> GeomNode:
    """A plain 1 x 1 x 1 cube centered on the origin (used for bullets)."""
    mesh = MeshBuilder()
    mesh.box(Vec3(0, 0, 0), Vec3(1, 1, 1), (1, 1, 1, 1))
    return mesh.build(name)


def load_drawing(name: str) -> tuple[list[str], Palette]:
    """Read `models/<name>.json` (read again every time, so edited files show up with "Reload models")."""
    data, source = _read_drawing(name)
    return parse_drawing(data, source)


def load_voxels(name: str) -> Voxels:
    """A model's cubes, from `models/<name>.json`: a flat drawing, a 3D (layered) one, or a MagicaVoxel model (read
    again every time, so edited files show up with "Reload models").
    """
    data, source = _read_drawing(name)
    return parse_voxels(data, source, name.rsplit("/", 1)[0] if "/" in name else "")


def load_engines(name: str) -> list[Engine]:
    data, source = _read_drawing(name)
    return parse_engines(data, source)


def _read_drawing(name: str) -> tuple[Any, str]:
    source = f"{name}.json"
    return json.loads((data_folder() / DRAWINGS_FOLDER / source).read_text()), source


def parse_voxels(data: Any, source: str = "drawing", folder: str = "") -> Voxels:
    """A model file in any of its forms (`folder`: where a .vox file it names is, within models/):
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
        return replace(_parse_layers(data, source), scale=_scale(data, source))
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


def _parse_layers(data: Any, source: str) -> Voxels:
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
        colors[char] = _palette_entry(char, {"color": entry["color"], "height": 1}, source)[0]
    return colors


def voxels_from_vox(model: vox.VoxModel) -> Voxels:
    """A MagicaVoxel model lying on the ground, seen from above: its x across, its y up the screen, its z up
    towards the camera.
    """
    size_x, size_y, size_z = model.size
    cells = {}
    for x, y, z, index in model.voxels:
        red, green, blue, _ = model.palette[index - 1]
        cells[x, size_y - 1 - y, size_z // 2 - z] = (red / 255, green / 255, blue / 255, 1.0)
    return Voxels(cells, size_x, size_y)


def voxels_to_vox(voxels: Voxels) -> vox.VoxModel:
    """The other way (for editing a model in MagicaVoxel): the same cubes, the same colors (up to 255 of them)."""
    layers = [layer for _, _, layer in voxels.cells] or [0]
    size_z = 2 * max(abs(min(layers)), abs(max(layers))) + 1
    palette: dict[tuple[int, int, int, int], int] = {}
    points = []
    for (column, row, layer), color in voxels.cells.items():
        rgba = (round(color[0] * 255), round(color[1] * 255), round(color[2] * 255), 255)
        index = palette.setdefault(rgba, len(palette) + 1)
        if index > 255:
            raise VoxelDrawingError.malformed("vox", "more than 255 colors")
        points.append((column, voxels.height - 1 - row, size_z // 2 - layer, index))
    return vox.VoxModel((voxels.width, voxels.height, size_z), points, list(palette))


def parse_drawing(data: Any, source: str = "drawing") -> tuple[list[str], Palette]:
    """A drawing file: "rows" (the drawing, one string per row, "." or " " for no voxel) and "palette" (for each
    character, its "color" as red, green, blue from 0 to 1 and its "height": how many voxels thick it is, odd).
    It can also have "engines" (see `parse_engines`).
    """
    if not isinstance(data, dict) or not DRAWING_KEYS <= set(data) <= DRAWING_KEYS | OPTIONAL_DRAWING_KEYS:
        keys = f"{sorted(DRAWING_KEYS)} and maybe {sorted(OPTIONAL_DRAWING_KEYS)}"
        raise VoxelDrawingError.malformed(source, f"expected the keys {keys}")
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
            red, green, blue, _ = _palette_entry("e", {"color": entry["color"], "height": 1}, source)[0]
            color = (red, green, blue, 1.0)
        z = entry.get("z", 0.0)
        if not isinstance(z, int | float) or isinstance(z, bool):
            raise VoxelDrawingError.malformed(source, f"{where}: 'z' must be a number")
        x, y, width, length = (float(value) for value in numbers)
        engines.append(Engine(x, y, width, length, entry["towards"], color, float(z)))
    return engines


def drawing_model(name: str) -> NodePath:
    """The drawing's voxel model, with a flame (a child node named "flame") for each of its engines."""
    data, source = _read_drawing(name)
    voxels = parse_voxels(data, source, name.rsplit("/", 1)[0] if "/" in name else "")
    mesh = MeshBuilder()
    mesh.drawn_cells(voxels, voxels.size)
    model = NodePath(mesh.build(name))
    for engine in parse_engines(data, source):
        add_flame(model, engine, (voxels.width, voxels.height), voxels.size)
    return model


def add_flame(model: NodePath, engine: Engine, shape: tuple[int, int], size: float) -> NodePath:
    """A flame under `model` at `engine`'s nozzle, `shape` being the model's (columns, rows) and `size` its voxel
    size.

    Its length is its Z scale: the game makes it flicker by changing it.
    """
    columns, rows = shape
    x = (engine.x - (columns - 1) / 2) * size
    edge = engine.y + (0.5 if engine.towards == "bottom" else -0.5)  # the side of the voxel the flame leaves from
    z = ((rows - 1) / 2 - edge) * size
    flame = model.attachNewNode("flame")
    flame.setPos(x, -engine.z * size, z)
    flame.setR(FLAME_DIRECTIONS[engine.towards])
    flame.setScale(engine.width * size, engine.width * size, engine.length * size)
    for part, color, scale in (("glow", engine.color, (1.0, 1.0)), ("core", FLAME_CORE_COLOR, FLAME_CORE_SIZE)):
        node = flame.attachNewNode(part)
        for heading in (0, 90):  # two crossed cards: it still looks like a flame when the ship banks
            card = node.attachNewNode(_flame_card())
            card.setH(heading)
        node.setScale(scale[0], scale[0], scale[1])
        node.setColor(*color)
    flame.setTexture(_flame_texture())
    flame.setLightOff()
    flame.setShaderOff()
    flame.setTwoSided(True)
    flame.setDepthWrite(False)
    flame.setBin("fixed", 15)  # after the ships, before the bullets
    flame.setAttrib(
        ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
    )
    return flame


def _flame_card() -> PandaNode:
    card = CardMaker("flame_card")
    card.setFrame(-0.5, 0.5, -1.0, 0.0)  # from the nozzle (Z 0) down to the tip (Z -1)
    return card.generate()


_FLAME_TEXTURES: list[Texture] = []


def _flame_texture() -> Texture:
    """White, with the flame's shape in its alpha: widest and brightest at the nozzle (the top row), narrowing and
    fading out towards the tip, soft at the edges. Built once.
    """
    if _FLAME_TEXTURES:
        return _FLAME_TEXTURES[0]
    width, height = FLAME_TEXTURE_SIZE
    image = PNMImage(width, height, 4)
    for row in range(height):
        along = row / (height - 1)  # 0 at the nozzle, 1 at the tip
        half_width = max((1 - along) ** 0.3, 1e-6)
        for column in range(width):
            across = abs((column + 0.5) / width * 2 - 1)
            edge = max(0.0, 1 - (across / half_width) ** 2)
            image.setXelA(column, row, 1, 1, 1, edge * (1 - along) ** 0.9)
    texture = Texture("flame")
    texture.load(image)
    texture.setWrapU(Texture.WM_clamp)
    texture.setWrapV(Texture.WM_clamp)
    _FLAME_TEXTURES.append(texture)
    return texture


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
    size = config.MODEL_VOXEL
    base = MeshBuilder()
    base.voxels(rows, palette, size)
    barrel = MeshBuilder()
    # Starts at the center of the dome and points down the screen, just in front of the dome.
    in_front = (thickest(palette) + thickest(barrel_palette)) / 2
    barrel_center = Vec3(0, -in_front * size, -len(barrel_rows) / 2 * size)
    barrel.voxels(barrel_rows, barrel_palette, size, barrel_center)
    model = NodePath(base.build("turret"))
    model.attachNewNode(barrel.build("barrel"))
    return model


def flak_cannon_model() -> NodePath:
    return drawing_model("flak_cannon")


def tank_model() -> NodePath:
    """Hull plus a separate child node named "barrel" (the turret: dome and gun) that the game turns toward the
    player, around the dome's middle. The hull's treads run along the top and bottom: it drives sideways.
    """
    size = config.MODEL_VOXEL
    hull_rows, hull_palette = load_drawing("tank")
    dome_rows, dome_palette = load_drawing("tank_turret")
    barrel_rows, barrel_palette = load_drawing("tank_barrel")
    hull = MeshBuilder()
    hull.voxels(hull_rows, hull_palette, size)
    turret = MeshBuilder()
    # The dome sits on the hull (half sunk into it); the gun starts at its middle and points down the screen.
    dome_depth = -thickest(hull_palette) / 2 * size
    turret.voxels(dome_rows, dome_palette, size, Vec3(0, dome_depth, 0))
    barrel_depth = dome_depth - thickest(dome_palette) / 4 * size
    turret.voxels(barrel_rows, barrel_palette, size, Vec3(0, barrel_depth, -len(barrel_rows) / 2 * size))
    model = NodePath(hull.build("tank"))
    model.attachNewNode(turret.build("barrel"))
    return model


def rocket_truck_model() -> NodePath:
    return drawing_model("rocket_truck")


def rocketeer_model() -> NodePath:
    return drawing_model("rocketeer")


def hunter_model() -> NodePath:
    return drawing_model("hunter")


def missile_silo_model() -> NodePath:
    return drawing_model("missile_silo")


def bomber_model() -> NodePath:
    return drawing_model("bomber")


def lancer_model() -> NodePath:
    return drawing_model("lancer")


def serpent_model() -> NodePath:
    return drawing_model("serpent")


def buckshot_model() -> NodePath:
    return drawing_model("buckshot")


def rocket_model() -> NodePath:
    return drawing_model("rocket")


def homing_missile_model() -> NodePath:
    return drawing_model("homing_missile")


def cluster_bomb_model() -> NodePath:
    return drawing_model("cluster_bomb")


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

    The capsule's drawing is in shades of grey, multiplied by the pickup's color.
    """
    rows, palette = load_drawing("capsule")
    tinted = {char: (tint(grey, color), height) for char, (grey, height) in palette.items()}
    model = voxel_model(f"pickup_{letter}", rows, tinted)
    extent = max(len(rows[0]), len(rows)) * config.MODEL_VOXEL
    text = TextNode("letter")
    text.setText(letter)
    text.setAlign(TextNode.ACenter)
    text.setTextColor(0.05, 0.05, 0.1, 1)
    label = model.attachNewNode(text)
    label.setScale(0.75 * extent)
    label.setPos(0, 0, -0.27 * extent)  # on the spin axis, so it stays centered while the capsule turns
    label.setBillboardPointEye()
    label.setLightOff()
    label.setShaderOff()
    # Drawn after everything else and without a depth test, so the capsule never hides it.
    label.setBin("fixed", 0)
    label.setDepthTest(False)
    label.setDepthWrite(False)
    return model


def gun_turret_model() -> NodePath:
    """The player's machine-gun turret, sitting on the ship: a dome plus a child node named "barrel" pointing down
    the screen (-Z), which the game turns toward what the turret shoots at.
    """
    size = config.MODEL_VOXEL
    dome = MeshBuilder()
    dome.ellipsoid(Vec3(0, 0, 0), Vec3(3 * size, 2 * size, 3 * size), (0.4, 0.75, 0.35, 1))
    barrel = MeshBuilder()
    barrel.box(Vec3(0, -1.5 * size, -3.5 * size), Vec3(1.2 * size, 1.2 * size, 7 * size), (0.25, 0.27, 0.3, 1))
    model = NodePath(dome.build("gun_turret"))
    model.attachNewNode(barrel.build("barrel"))
    return model


def lightning_coil_model() -> NodePath:
    """The lightning gun, sitting on the ship: a glowing violet orb."""
    size = config.MODEL_VOXEL
    mesh = MeshBuilder()
    mesh.ellipsoid(Vec3(0, 0, 0), Vec3(2.5 * size, 2.5 * size, 2.5 * size), (0.8, 0.6, 1.0, 1), rings=6, segments=10)
    orb = NodePath(mesh.build("lightning_coil"))
    orb.setLightOff()
    orb.setShaderOff()
    return orb


def repair_model() -> NodePath:
    return drawing_model("repair")


def extra_life_model() -> NodePath:
    return drawing_model("extra_life")


def laser_beam_model() -> NodePath:
    """The laser's bright core: a thin box, stretched to the beam's size (a 1 x 1 beam). The rest of the beam is
    light: streaks shooting up it (effects/laser.py) in a soft halo (effects_view.py).
    """
    mesh = MeshBuilder()
    mesh.box(Vec3(0, 0, 0), Vec3(0.25, 0.25, 1.0), (0.85, 1.0, 1.0, 0.95))
    beam = NodePath(mesh.build("laser"))
    beam.setTransparency(TransparencyAttrib.MAlpha)
    beam.setLightOff()
    beam.setShaderOff()
    return beam


# Backgrounds (background.py): asteroids and a distant planet, colored by the level's scenery.


def mottle(color: Color, cell: Cell, amount: float = 0.08) -> Color:
    """Slightly lighter or darker per voxel (always the same for a cell), so big flat areas aren't flat."""
    column, row, layer = cell
    noise = ((column * 73856093) ^ (row * 19349663) ^ (layer * 83492791)) % 1000 / 1000
    return shade(color, 1 + amount * (2 * noise - 1))


def rock_model(shape: int, colors: tuple[Color, ...]) -> NodePath:
    """A lumpy voxel asteroid of `colors`, the same for the same `shape`; fits the unit box."""
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
                    cells[cell] = mottle(rng.choice(colors), cell, 0.15)
    mesh = MeshBuilder()
    mesh.cells(cells, 1 / (2 * radius + 1), Vec3(0, 0, 0))
    return NodePath(mesh.build(f"rock_{shape}"))


def distant_planet_model(colors: tuple[Color, ...], seed: int = 7) -> NodePath:
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
