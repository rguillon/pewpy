"""The types the models are made of."""

import numpy as np
from numpy.typing import NDArray
from panda3d.core import Vec3

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
