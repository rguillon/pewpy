"""Building meshes: flat-shaded, colored triangles and voxels, turned into Panda3D geometry."""

import math

import numpy as np
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexData, GeomVertexFormat, Vec3

from pewpy.graphics.models.colors import shade
from pewpy.graphics.models.drawings.voxels import Voxels, voxel_cells
from pewpy.graphics.models.mesh.slopes import (
    CUT_SIDES,
    FACING_QUARTER,
    OPPOSITE,
    SLANT_NORMALS,
    cuts,
    face_quarters,
    slant,
)
from pewpy.graphics.models.mesh.voxel_faces import (
    CONTEXT,
    FACE_AXES,
    FACE_DIRECTIONS,
    OCCLUSION_BRIGHTNESS,
    Occupancy,
    corner_levels,
    face_corners,
    merged_faces,
    model_axes,
)
from pewpy.graphics.models.types import (
    UV,
    BoolArray,
    Cell,
    Color,
    Direction,
    FloatArray,
    IntArray,
    Outline,
    Palette,
    Vertex,
)

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
        """Add a flat triangle; `brightness` darkens each corner's color (the GPU blends it across the triangle)."""
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
        """Add a quad as two triangles, split along its brighter diagonal."""
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
        """Add a flat convex outline in the X/Z plane, extruded along Y (depth) from `y_front` to `y_back`."""
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
        """Add a box."""
        half_x, half_z = size.x / 2, size.z / 2
        outline = [(-half_x, -half_z), (half_x, -half_z), (half_x, half_z), (-half_x, half_z)]
        moved = [(center.x + x, center.z + z) for x, z in outline]
        self.prism(moved, center.y - size.y / 2, center.y + size.y / 2, color)

    def ellipsoid(self, center: Vec3, radii: Vec3, color: Color, rings: int = 4, segments: int = 8) -> None:
        """Add a low-poly sphere stretched by `radii` along X, Y and Z."""

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

        Works on every cube at once (numpy): which cubes are cut into 45° slopes (see `slopes`), which faces show, how
        dark their corners are, then whole faces that look alike are merged into rectangles (fewer triangles, same
        look, see `merged_faces`). Faces only partly there (cut, or partly covered by a cut neighbor) are drawn a
        quarter at a time.
        """
        if not cells:
            return
        # Positions in cubes along the model's X (column), Y (depth layer) and Z (up: minus the row).
        positions = model_axes(np.array(list(cells), dtype=np.int64))
        color_indices: dict[Color, int] = {}
        color_of = np.array([color_indices.setdefault(color, len(color_indices)) for color in cells.values()])
        colors = np.array(list(color_indices), dtype=np.float64)
        special = np.zeros(len(positions), dtype=np.int64)  # 0: plain voxel, 1: glowing, 2: burning
        if glowing or burning:
            special = np.array([2 if cell in burning else 1 if cell in glowing else 0 for cell in cells])
        occupancy = Occupancy(positions, model_axes(np.array(list(context), dtype=np.int64).reshape(-1, 3)))
        cut = cuts(positions, occupancy, special == 0)  # glowing and burning cubes stay whole
        quarters = face_quarters(cut)
        origin_array = np.array(origin, dtype=np.float64)
        for index, direction in enumerate(FACE_DIRECTIONS):
            normal, u, w = FACE_AXES[direction]
            neighbor = occupancy.at(positions + normal)
            covered = np.zeros((len(positions), 4), dtype=bool)  # by the neighbor's face, looking back
            drawn = neighbor >= 0
            covered[drawn] = quarters[neighbor[drawn], OPPOSITE[index]][:, FACING_QUARTER[index]]
            covered[neighbor == CONTEXT] = True
            exposed = quarters[:, index] & ~covered
            whole = exposed.all(axis=1)
            partial = exposed.any(axis=1) & ~whole
            for kind, uvs in ((1, GLOW_UVS), (2, BURN_UVS)):
                picked = whole & (special == kind)
                if picked.any():
                    self._single_faces(positions[picked], colors[color_of[picked]], uvs, direction, size, origin_array)
            plain = whole & (special == 0)
            if plain.any():
                face_positions, face_colors = positions[plain], color_of[plain]
                rectangles = merged_faces(
                    face_positions @ normal,
                    face_positions @ u,
                    face_positions @ w,
                    face_colors,
                    corner_levels(face_positions, direction, occupancy),
                )
                self._rectangles(rectangles, colors, direction, size, origin_array)
            if partial.any():
                kinds = special[partial]
                brightness = np.ones((len(kinds), 4))
                lit = kinds == 0
                levels = corner_levels(positions[partial][lit], direction, occupancy)
                brightness[lit] = np.array(OCCLUSION_BRIGHTNESS)[levels]
                uvs = np.array([QUAD_UVS, GLOW_UVS, BURN_UVS], dtype=np.float64)[kinds]
                self._quarters(
                    positions[partial],
                    exposed[partial],
                    colors[color_of[partial]],
                    brightness,
                    uvs,
                    direction,
                    size,
                    origin_array,
                )
        self._slants(positions, cut, colors[color_of], size, origin_array)

    def _rectangles(
        self, rectangles: IntArray, colors: FloatArray, direction: Direction, size: float, origin: FloatArray
    ) -> None:
        """Add the rectangles from `merged_faces` lying in the planes facing `direction`."""
        normal, u, w = FACE_AXES[direction]
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
        """Add a face per cube, not merged nor shaded (glowing and burning faces: the shader draws each as a pane)."""
        count = len(positions)
        corner_uvs = np.broadcast_to(np.array(uvs, dtype=np.float64), (count, 4, 2))
        corners = face_corners(positions, direction, size, origin)
        self._faces(corners, colors, np.ones((count, 4)), corner_uvs, FACE_AXES[direction][0])

    def _quarters(
        self,
        positions: IntArray,
        exposed: BoolArray,
        colors: FloatArray,
        brightness: FloatArray,
        uvs: FloatArray,
        direction: Direction,
        size: float,
        origin: FloatArray,
    ) -> None:
        """Add the `exposed` quarters of the faces of cubes looking along `direction` (see `slopes`).

        Two quarters side by side make a triangle (half the face); others are drawn each as a triangle to the face's
        middle, which gets the average of its corners' shading and texture coordinates.
        """
        normal = FACE_AXES[direction][0]
        corners = face_corners(positions, direction, size, origin)
        # Corners 0 to 3, then the middle (4).
        points = np.concatenate([corners, corners.mean(axis=1, keepdims=True)], axis=1)
        lights = np.concatenate([brightness, brightness.mean(axis=1, keepdims=True)], axis=1)
        coordinates = np.concatenate([uvs, uvs.mean(axis=1, keepdims=True)], axis=1)
        halves = (exposed.sum(axis=1) == 2) & (exposed & np.roll(exposed, -1, axis=1)).any(axis=1)
        faces, picks = [], []
        for quarter in range(4):
            half = np.flatnonzero(halves & exposed[:, quarter] & exposed[:, (quarter + 1) % 4])
            alone = np.flatnonzero(~halves & exposed[:, quarter])
            after, next_after = (quarter + 1) % 4, (quarter + 2) % 4
            for chosen, triangle in ((half, (quarter, after, next_after)), (alone, (quarter, after, 4))):
                faces.append(chosen)
                picks.append(np.broadcast_to(np.array(triangle), (len(chosen), 3)))
        face = np.concatenate(faces)
        pick = np.concatenate(picks)
        self._add(
            points[face[:, None], pick],
            np.broadcast_to(normal.astype(np.float64), (len(face), 3)),
            colors[face],
            lights[face[:, None], pick],
            coordinates[face[:, None], pick],
        )

    def _slants(self, positions: IntArray, cut: BoolArray, colors: FloatArray, size: float, origin: FloatArray) -> None:
        """Add the slanted faces of the cubes cut into slopes (`colors`: each cube's), a triangle fan each."""
        corners, normals, triangle_colors, uvs = [], [], [], []
        for cube in np.flatnonzero(cut.any(axis=1)).tolist():
            for index in np.flatnonzero(cut[cube]).tolist():
                polygon = slant(cut[cube], index)  # at least a triangle: no cuts a cube can have trim a slant away
                a, b = CUT_SIDES[index]
                across, along = a - b, np.cross(a, b)
                coordinates = np.stack([(polygon @ across + 1) / 2, polygon @ along + 0.5], axis=1)
                points = origin + (positions[cube] + polygon) * size
                for second in range(1, len(polygon) - 1):
                    corners.append(points[[0, second, second + 1]])
                    uvs.append(coordinates[[0, second, second + 1]])
                    normals.append(SLANT_NORMALS[index])
                    triangle_colors.append(colors[cube])
        if corners:
            self._add(
                np.array(corners),
                np.array(normals),
                np.array(triangle_colors),
                np.ones((len(corners), 3)),
                np.array(uvs),
            )

    def _faces(
        self, corners: FloatArray, colors: FloatArray, brightness: FloatArray, uvs: FloatArray, normal: IntArray
    ) -> None:
        """Add faces from their 4 corners (winding counter-clockwise seen from outside).

        Each is split in two triangles along the brighter diagonal, or the shading would show a crease across the face
        (like `quad`).
        """
        crease = brightness[:, 0] + brightness[:, 2] < brightness[:, 1] + brightness[:, 3]
        # Which corners make each face's two triangles: (a, b, d) and (b, c, d), or (a, b, c) and (a, c, d).
        picks = np.where(crease[:, None, None], [[0, 1, 3], [1, 2, 3]], [[0, 1, 2], [0, 2, 3]]).reshape(-1, 3)
        faces = np.repeat(np.arange(len(corners)), 2)  # the face of each triangle
        self._add(
            corners[faces[:, None], picks],
            np.broadcast_to(normal.astype(np.float64), (len(picks), 3)),
            colors[faces],
            brightness[faces[:, None], picks],
            uvs[faces[:, None], picks],
        )

    def _add(
        self, corners: FloatArray, normals: FloatArray, colors: FloatArray, brightness: FloatArray, uvs: FloatArray
    ) -> None:
        """Add triangles, each with its own color darkened at each corner by `brightness` (like `shade`).

        Corners (n, 3, 3) wind counter-clockwise seen from outside; normals (n, 3), colors (n, 4), brightness (n, 3),
        corner texture coordinates (n, 3, 2).
        """
        rgb = np.minimum(colors[:, None, :3] * brightness[..., None], 1.0)
        alpha = np.broadcast_to(colors[:, None, 3:], (len(colors), 3, 1))
        self._blocks.append((corners, normals, np.concatenate([rgb, alpha], axis=2), uvs))

    def build(self, name: str) -> GeomNode:
        """Build the mesh as a node."""
        positions, normals, colors, uvs = self._arrays()
        count = len(positions) * 3
        # One vertex as the GPU gets it: GeomVertexFormat.getV3n3c4t2(), a single interleaved array of 36 bytes
        # (position, normal: 3 floats each; color: 4 bytes; uv: 2 floats).
        # Colors are stored as bytes; Panda3D converts a float the same way (in 32 bits, rounding down).
        color_bytes = np.clip(np.floor(colors.reshape(-1, 4).astype(np.float32) * np.float32(255)), 0, 255)
        fields = (
            positions.reshape(-1, 3).astype("<f4"),
            np.repeat(normals, 3, axis=0).astype("<f4"),
            color_bytes.astype(np.uint8),
            uvs.reshape(-1, 2).astype("<f4"),
        )
        vertices = np.concatenate(
            [field.view(np.uint8).reshape(count, field.shape[1] * field.itemsize) for field in fields], axis=1
        )
        data = GeomVertexData(name, GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
        data.uncleanSetNumRows(count)
        primitive = GeomTriangles(Geom.UHStatic)
        if count:
            data.modifyArrayHandle(0).copyDataFrom(vertices)
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
