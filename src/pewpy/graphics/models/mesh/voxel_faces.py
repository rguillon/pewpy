"""Working out voxel faces in bulk (numpy).

Which show, how dark their corners are (ambient occlusion), and merging faces that look alike into rectangles.
"""

import numpy as np

from pewpy.graphics.models.types import BoolArray, Direction, IntArray

FACE_DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
# Ambient occlusion: brightness of a voxel face corner touched by 0, 1, 2 or 3 neighbor voxels in front of the face.
# Darkens inner corners and creases so the blocks read as separate cubes.
OCCLUSION_BRIGHTNESS = (1.0, 0.8, 0.66, 0.55)
# The 4 corners of a voxel face, as steps along its two axes (u, w), in winding order.
FACE_CORNERS = ((-1, -1), (1, -1), (1, 1), (-1, 1))


def face_axes(direction: Direction) -> tuple[IntArray, IntArray, IntArray]:
    """Return the normal of a voxel face looking along `direction` and two axes along the face (u, w), in cubes.

    u x w is the normal, so corners taken along u then w wind counter-clockwise seen from outside.
    """
    normal = np.array(direction, dtype=np.int64)
    u = np.array((0, 0, 1) if direction[0] else (1, 0, 0), dtype=np.int64)
    return normal, u, np.cross(normal, u)


FACE_AXES = {direction: face_axes(direction) for direction in FACE_DIRECTIONS}


def model_axes(cells: IntArray) -> IntArray:
    """Cells (column, row, layer) as positions in cubes along the model's X, Y (depth) and Z (up the screen)."""
    return np.stack([cells[:, 0], cells[:, 2], -cells[:, 1]], axis=1) if len(cells) else np.zeros((0, 3), np.int64)


class Occupancy:
    """Which cube positions hold a voxel (drawn or context), as a 3D grid: one lookup for many positions at once."""

    def __init__(self, drawn: IntArray, context: IntArray) -> None:
        everything = np.concatenate([drawn, context])
        self.low = everything.min(axis=0) - 1  # neighbors are at most one cube away along each axis
        self.grid = np.zeros(everything.max(axis=0) - self.low + 2, dtype=bool)
        self.grid[tuple((everything - self.low).T)] = True

    def filled(self, positions: IntArray) -> BoolArray:
        """Tell, for each position, whether a voxel is there."""
        return self.grid[tuple((positions - self.low).T)]


def occlusion_level(side_a: BoolArray, side_b: BoolArray, corner: BoolArray) -> IntArray:
    """Count how many voxels touch voxel face corners (0 to 3).

    From the cells in front of each face along its two edges (`side_a`, `side_b`) and diagonally (`corner`). With both
    sides filled the corner is fully tucked in (3), whatever the diagonal. OCCLUSION_BRIGHTNESS gives the brightness of
    each level.
    """
    return np.where(side_a & side_b, 3, side_a.astype(np.int64) + side_b + corner)


def merged_faces(depth: IntArray, along_u: IntArray, along_w: IntArray, colors: IntArray, levels: IntArray) -> IntArray:
    """Cover faces facing the same way with as few rectangles as possible (greedy meshing).

    Each rectangle is made of faces with the same color and corner shading. Faces are given by their plane (`depth`),
    place in it (`along_u`, `along_w`, in cubes), color index and corner occlusion levels (n, 4). A rectangle grows
    along u, then w, from its first face in (depth, u, w) order, and only along a direction where its shading doesn't
    change, so the GPU blends it the same as the faces it replaces. Returns rows of (depth, u, w, width, height, color,
    4 corner levels).
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
