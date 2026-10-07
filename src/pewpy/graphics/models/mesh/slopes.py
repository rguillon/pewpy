"""45° slopes where voxels form a staircase (numpy): which cubes are cut in half, and what is left of their faces.

A cube on the outer corner of a step is cut along the diagonal plane through its middle, across the edge between its
two open faces: the half towards the open side goes. Cut cubes keep the other half, so a stair of cubes reads as a
straight slanted line. Every cut keeps whole quarters of a cube's faces (the triangles from the face's middle to each
of its edges), so faces are worked out a quarter at a time.
"""

import math

import numpy as np

from pewpy.graphics.models.mesh.voxel_faces import FACE_AXES, FACE_DIRECTIONS, Occupancy
from pewpy.graphics.models.types import BoolArray, FloatArray, IntArray

# The cuts a cube can have: one per edge, given by its two open sides (a, b). A cut keeps (a + b) . p <= 0, p measured
# from the cube's middle: the half away from that edge.
CUTS = tuple(
    (tuple(sign_a * (axis == i) for axis in range(3)), tuple(sign_b * (axis == j) for axis in range(3)))
    for i in range(3)
    for j in range(i + 1, 3)
    for sign_a in (1, -1)
    for sign_b in (1, -1)
)
CUT_SIDES = np.array(CUTS, dtype=np.int64)  # (12, 2, 3)


def quarter_edges(direction: tuple[int, int, int]) -> IntArray:
    """Return the edge each quarter of a face along `direction` touches, in cubes; quarter k joins corners k, k + 1.

    Corners are FACE_CORNERS, so the quarters go: -w, +u, +w, -u.
    """
    _, u, w = FACE_AXES[direction]
    return np.array([-w, u, w, -u])


QUARTER_EDGES = np.array([quarter_edges(direction) for direction in FACE_DIRECTIONS])  # (6, 4, 3)
OPPOSITE = tuple(FACE_DIRECTIONS.index((-x, -y, -z)) for x, y, z in FACE_DIRECTIONS)
# For each direction, the quarter of the facing face (the neighbor's, looking back) that lies on each quarter.
FACING_QUARTER = np.array([
    [next(q for q in range(4) if (QUARTER_EDGES[OPPOSITE[d], q] == edge).all()) for edge in QUARTER_EDGES[d]]
    for d in range(len(FACE_DIRECTIONS))
])
# Which cuts take each quarter away: the ones its middle is on the wrong side of. (6, 4, 12)
QUARTER_CUT_BY = (
    np.einsum(
        "dqx,kx->dqk",
        np.array(FACE_DIRECTIONS)[:, None, :] / 2 + QUARTER_EDGES / 3,
        CUT_SIDES.sum(axis=1),
    )
    > 0
)


def cuts(positions: IntArray, occupancy: Occupancy, cuttable: BoolArray) -> BoolArray:
    """Tell, for each cube and each of CUTS, whether the cube is cut there: (n, 12).

    A cube is cut across an edge when its two sides there are open, the two opposite ones taken (it is a corner, not
    a lone spike) and the stair goes on: a cube one step further along it, past either side. A rectangle's corners
    don't go on, so they stay square.
    """
    result = np.zeros((len(positions), len(CUTS)), dtype=bool)
    for index in range(len(CUTS)):
        a, b = CUT_SIDES[index]
        filled = {
            step: occupancy.filled(positions + np.array(step)) for step in map(tuple, (a, b, -a, -b, a - b, b - a))
        }
        open_corner = ~filled[tuple(a)] & ~filled[tuple(b)] & filled[tuple(-a)] & filled[tuple(-b)]
        result[:, index] = cuttable & open_corner & (filled[tuple(a - b)] | filled[tuple(b - a)])
    return result


def face_quarters(cut: BoolArray) -> BoolArray:
    """Tell which quarters of each face are left on each cube, given its cuts: (n, 6 directions, 4 quarters)."""
    taken = cut.astype(np.int64) @ QUARTER_CUT_BY.reshape(-1, len(CUTS)).T
    return taken.reshape(len(cut), len(FACE_DIRECTIONS), 4) == 0


def slant_rectangle(index: int) -> FloatArray:
    """Return the slanted face of a cube with only the cut `index`: its 4 corners in cubes from the cube's middle.

    Wound counter-clockwise seen from outside (from the open edge).
    """
    a, b = CUT_SIDES[index]
    across, along = (a - b) / 2, np.cross(a, b) / 2  # across: from one kept edge to the other
    corners = np.array([across * s + along * t for s, t in ((1, -1), (1, 1), (-1, 1), (-1, -1))])
    if np.cross(corners[1] - corners[0], corners[2] - corners[0]) @ (a + b) < 0:
        corners = corners[::-1]
    return corners


CUT_NORMALS = CUT_SIDES.sum(axis=1)  # (12, 3), outwards, not normalized
SLANT_NORMALS = CUT_NORMALS / math.sqrt(2)
SLANT_RECTANGLES = np.array([slant_rectangle(index) for index in range(len(CUTS))])  # (12, 4, 3)


def clip(polygon: FloatArray, side: IntArray) -> FloatArray:
    """Cut a flat convex polygon (corners (n, 3), in cubes from the cube's middle) to the half where side . p <= 0."""
    result = []
    heights = polygon @ side
    for index, point in enumerate(polygon):
        after = (index + 1) % len(polygon)
        here, there = heights[index], heights[after]
        if here <= 0:
            result.append(point)
        if (here < 0 < there) or (there < 0 < here):
            result.append(point + (polygon[after] - point) * (here / (here - there)))
    return np.array(result).reshape(-1, 3)


def slant(cut: BoolArray, index: int) -> FloatArray:
    """Return the slanted face a cube's cut `index` leaves, trimmed by its other `cut`s: (n, 3), see slant_rectangle."""
    polygon = SLANT_RECTANGLES[index]
    for other in np.flatnonzero(cut):
        if other != index:
            polygon = clip(polygon, CUT_NORMALS[other])
    return polygon
