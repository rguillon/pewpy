"""Smooth grounds: a continuous height field (see terrain.py).

A relief is a grid of heights (world units, rising towards the camera from the ground's base layer) sampled every
`step` world units, looping along the rows: the row after the last one is row 0 again.
It also has each point's normal, how tucked-in it is (`cavity`: valleys and hollows get less sky light) and the
shadows of a low sun, which the ground shader (shader/) uses with the height and slope to paint it.

On grounds with a fluid (water, lava, or the gaps of a cloud deck), everything below height 0 is under it: the
surface is flat there and `depth` says how deep it is. A landscape can also mark each point with a number from 0 to
1 (`marks`: forest or clearing, reeds or mud...) for the shader. The landscapes are in grounds/ (see landscapes.py).

Numpy only, independent from Panda3D.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatGrid = NDArray[np.float64]


@dataclass
class Shape:
    """What a landscape makes: heights (below 0: under the fluid, if there is one) and marks (0 to 1)."""

    heights: FloatGrid
    marks: FloatGrid | None = None


# (rng, rows, columns, highest point in world units, step) -> the shape
ReliefGenerator = Callable[[np.random.Generator, int, int, float, float], Shape]

RELIEF_STEP = 0.02  # world units between two points of the grid (about: whole chunks must fit exactly)
CAVITY_RADIUS = 6  # grid points: a point lower than its surroundings within this distance is in a hollow
# The sun, low in the top-left of the screen: its direction along the ground (x right, y down the screen) and how
# high it is (rise per unit of distance). Shadows are baked from it; the ground shader lights with the same sun.
SUN_ALONG = (-0.7071, -0.7071)
SUN_RISE = 0.6
SHADOW_REACH = 1.2  # world units: how far a peak's shadow can fall
SHADOW_SOFTNESS = 0.015  # world units of height over which a shadow's edge fades


@dataclass
class Relief:
    """A ground's relief: its heights, fluid depth, marks, normals, shading and shadows."""

    heights: FloatGrid  # (rows, columns), world units above the base layer (the surface: a fluid is flat at 0)
    # (rows, columns): how deep the fluid is; on land, negative: how far above it (the shader finds the shore
    # between two points where this changes sign, rather than on a point of the grid).
    depth: FloatGrid
    marks: FloatGrid  # (rows, columns), 0 to 1, the landscape's own meaning
    normals: FloatGrid  # (rows, columns, 3): x right, y down the rows (down the screen), z up towards the camera
    cavity: FloatGrid  # (rows, columns), 0 (out in the open) to 1 (deep in a hollow)
    shadow: FloatGrid  # (rows, columns), 0 (in the sun) to 1 (in the shadow of higher ground)
    # (rows, columns): below this height, a point there is in the shadow of something (the ground, or props
    # standing on it): the shaders use it for props too, and shade walls and roofs pixel by pixel.
    shadow_heights: FloatGrid
    step_x: float
    step_y: float

    @property
    def rows(self) -> int:
        """The number of rows of the grid."""
        return self.heights.shape[0]

    @property
    def columns(self) -> int:
        """The number of columns of the grid."""
        return self.heights.shape[1]


def periodic_noise(rng: np.random.Generator, rows: int, columns: int, cell: float) -> FloatGrid:
    """Make smooth value noise from 0 to 1 on a (rows, columns) grid, a random value about every `cell` points.

    It loops along the rows (the cell is stretched a little so a whole number of them fits the loop).
    """
    lattice_rows = max(round(rows / cell), 1)
    y = np.arange(rows) * lattice_rows / rows
    x = np.arange(columns) / cell
    lattice = rng.random((lattice_rows, int(x[-1]) + 2))
    y0 = np.floor(y).astype(np.int64)
    x0 = np.floor(x).astype(np.int64)
    ty = _smooth(y - y0)[:, None]
    tx = _smooth(x - x0)[None, :]
    near, far = lattice[y0 % lattice_rows], lattice[(y0 + 1) % lattice_rows]
    top = near[:, x0] * (1 - tx) + near[:, x0 + 1] * tx
    bottom = far[:, x0] * (1 - tx) + far[:, x0 + 1] * tx
    return top * (1 - ty) + bottom * ty


def ridged_mountains(rng: np.random.Generator, rows: int, columns: int, cell: float, octaves: int = 6) -> FloatGrid:
    """Make ridged multifractal noise from 0 to 1: sharp ridges and valleys, finer ridges mostly on the high ground.

    Each octave is weighted by the one before, like eroded mountains.
    """
    total = np.zeros((rows, columns))
    weight = np.ones((rows, columns))
    amplitude, norm = 1.0, 0.0
    for _ in range(octaves):
        ridge = (1.0 - np.abs(2.0 * periodic_noise(rng, rows, columns, cell) - 1.0)) ** 2
        ridge *= weight
        weight = np.clip(ridge * 2.0, 0.0, 1.0)
        total += ridge * amplitude
        norm += amplitude
        amplitude *= 0.5
        cell = max(cell / 2, 1.5)
    return total / norm


def eroded_noise(rng: np.random.Generator, rows: int, columns: int, cell: float, octaves: int = 7) -> FloatGrid:
    """Make layered noise where each finer layer is damped where the layers before it are steep.

    Slopes stay smooth and detail gathers on crests and valley floors, a cheap look of erosion (branching valleys rather
    than blobs).
    """
    total = np.zeros((rows, columns))
    slope_x, slope_y = np.zeros_like(total), np.zeros_like(total)
    amplitude, norm = 1.0, 0.0
    for _ in range(octaves):
        layer = periodic_noise(rng, rows, columns, cell) - 0.5
        gy = (np.roll(layer, -1, axis=0) - np.roll(layer, 1, axis=0)) / 2 * cell
        gx = np.gradient(layer, axis=1) * cell
        slope_x += gx * amplitude
        slope_y += gy * amplitude
        total += amplitude * layer / (1.0 + slope_x**2 + slope_y**2)
        norm += amplitude
        amplitude *= 0.5
        cell = max(cell / 2, 1.5)
    return total / norm


def make_relief(
    shape: Shape, step_x: float, step_y: float, occluders: FloatGrid | None = None, fluid: bool = False
) -> Relief:
    """Make a landscape's relief: its normals, cavity and shadows (looping along the rows).

    `occluders`: the heights with what stands on the ground (buildings, trees): they cast shadows and make hollows too.
    `fluid`: below 0 is under a flat fluid.
    """
    depth = -shape.heights if fluid else np.full_like(shape.heights, -1.0)
    heights = np.maximum(shape.heights, 0.0) if fluid else shape.heights
    marks = shape.marks if shape.marks is not None else np.zeros_like(heights)
    # Slopes: rows loop (np.roll), columns don't (edges use one-sided differences).
    dz_dy = (np.roll(heights, -1, axis=0) - np.roll(heights, 1, axis=0)) / (2 * step_y)
    dz_dx = np.gradient(heights, step_x, axis=1)
    # The rows go down the screen (y); heights rise towards the camera (z).
    normals = np.stack([-dz_dx, -dz_dy, np.ones_like(heights)], axis=-1)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    solid = heights if occluders is None else np.maximum(heights, occluders)
    shadow_heights = _shadow_heights(solid, step_x, step_y)
    shadow = np.clip((shadow_heights - heights) / SHADOW_SOFTNESS + 0.5, 0.0, 1.0)
    cavity = _cavity(heights, solid)
    return Relief(heights, depth, marks, normals, cavity, shadow, shadow_heights, step_x, step_y)


def _shadow_heights(solid: FloatGrid, step_x: float, step_y: float) -> FloatGrid:
    """Return how high the shadows reach at every point.

    March towards the sun, a grid point at a time along the diagonal, and keep the highest sun ray passing over what's
    there.
    """
    columns = solid.shape[1]
    step = math.hypot(step_x, step_y)
    reach = np.full_like(solid, -1.0)
    column_index = np.arange(columns)
    for k in range(1, int(SHADOW_REACH / step) + 1):
        # The point k steps towards the sun: up the rows (they loop) and to the left (clamped at the edge).
        ahead = np.roll(solid, k, axis=0)[:, np.clip(column_index - k, 0, columns - 1)]
        reach = np.maximum(reach, ahead - k * step * SUN_RISE)
    return reach


def _cavity(heights: FloatGrid, solid: FloatGrid) -> FloatGrid:
    """Return how much lower each point is than the average of what's around it, scaled to 0-1.

    `solid` is the heights with the props; the average is a box filter.
    """
    blurred = solid
    for axis in (0, 1):
        total = np.zeros_like(blurred)
        for offset in range(-CAVITY_RADIUS, CAVITY_RADIUS + 1):
            if axis == 0:
                total += np.roll(blurred, offset, axis=0)
            else:
                total += np.take(
                    blurred, np.clip(np.arange(blurred.shape[1]) + offset, 0, blurred.shape[1] - 1), axis=1
                )
        blurred = total / (2 * CAVITY_RADIUS + 1)
    depth = np.maximum(blurred - heights, 0.0)
    scale = np.percentile(depth, 98) or 1.0
    return np.clip(depth / scale, 0.0, 1.0)


def smoothstep(edge0: float, edge1: float, x: FloatGrid) -> FloatGrid:
    """Return 0 below `edge0`, 1 above `edge1`, and a smooth curve between."""
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _smooth(t: FloatGrid) -> FloatGrid:
    return t * t * t * (t * (t * 6 - 15) + 10)
