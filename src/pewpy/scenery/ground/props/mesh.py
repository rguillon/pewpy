"""The mesh every prop is built into (see __init__.py), and its shapes: boxes, cylinders, discs, ellipsoids, gabled
roofs, shapes turned on a lathe.

Built in bulk with numpy as plain arrays (the ground's shader/ turns them into Panda3D geometry). Every vertex has
14 floats: position (3), normal (3), color (red, green, blue, material) and texture data (4: along the wall,
up the wall, the prop's seed from 0 to 1, unused). The material tells the prop shader how to paint a face (see
MATERIALS); the wall coordinates, in world units, place the windows.

Props are built in ground coordinates (x right, y down the loop, z up towards the camera), then turned into a
strip's model space (x right, y away from the camera, z up the screen) by `strip_arrays`.
Their colors come from the level's scenery (`props`, see pewpy.scenery.params). Independent from Panda3D.
"""

import itertools
import math
import random

import numpy as np
from numpy.typing import NDArray

from pewpy.scenery.ground.settlement import Prop

Color = tuple[float, float, float]
FloatArray = NDArray[np.float32]
IndexArray = NDArray[np.uint32]

# How the prop shader paints a face (the color's 4th number).
PLAIN, OFFICE, HOMES, FURNACE, LIGHT, FOLIAGE, METAL, ROOFING = range(8)

SUNK = 0.01  # walls go this far below their base, so no gap shows on slopes


class PropMesh:
    def __init__(self) -> None:
        self.vertices: list[FloatArray] = []
        self.indices: list[IndexArray] = []
        self.count = 0
        self.seed = 0.0  # the prop being built (0 to 1): the shader picks its lit windows with it

    def _add(self, vertices: FloatArray, indices: IndexArray) -> None:
        self.vertices.append(vertices)
        self.indices.append(indices + self.count)
        self.count += len(vertices)

    def quad(
        self,
        corners: list[tuple[float, float, float]],
        normal: tuple[float, float, float],
        color: Color,
        material: int,
        wall: list[tuple[float, float]] | None = None,
    ) -> None:
        vertices = np.zeros((4, 14), dtype=np.float32)
        vertices[:, 0:3] = corners
        vertices[:, 3:6] = normal
        vertices[:, 6:9] = color
        vertices[:, 9] = material
        if wall is not None:
            vertices[:, 10:12] = wall
        vertices[:, 12] = self.seed
        self._add(vertices, np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32))

    def box(
        self,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        z0: float,
        z1: float,
        color: Color,
        material: int,
        top: Color | None = None,
        top_material: int = PLAIN,
    ) -> None:
        """Four walls (their windows counted from z0) and a flat top."""
        z_low = z0 - SUNK
        for (ax, ay), (bx, by), normal in (
            ((x0, y0), (x1, y0), (0.0, -1.0, 0.0)),  # the side towards the top of the screen
            ((x1, y0), (x1, y1), (1.0, 0.0, 0.0)),
            ((x1, y1), (x0, y1), (0.0, 1.0, 0.0)),
            ((x0, y1), (x0, y0), (-1.0, 0.0, 0.0)),
        ):
            length = math.hypot(bx - ax, by - ay)
            corners = [(ax, ay, z_low), (bx, by, z_low), (bx, by, z1), (ax, ay, z1)]
            self.quad(corners, normal, color, material, [(0, -SUNK), (length, -SUNK), (length, z1 - z0), (0, z1 - z0)])
        self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0.0, 0.0, 1.0), top or color, top_material)

    def cylinder(
        self,
        x: float,
        y: float,
        radius: float,
        z0: float,
        z1: float,
        color: Color,
        material: int,
        top: Color | None = None,
        segments: int = 14,
    ) -> None:
        """Upright, smooth-shaded, with a flat top."""
        angles = np.linspace(0, 2 * np.pi, segments + 1)
        cos, sin = np.cos(angles), np.sin(angles)
        ring = segments + 1
        vertices = np.zeros((2 * ring, 14), dtype=np.float32)
        for level, z in enumerate((z0 - SUNK, z1)):
            part = vertices[level * ring : (level + 1) * ring]
            part[:, 0] = x + radius * cos
            part[:, 1] = y + radius * sin
            part[:, 2] = z
            part[:, 3] = cos
            part[:, 4] = sin
            part[:, 10] = angles * radius
            part[:, 11] = z - z0
        vertices[:, 6:9] = color
        vertices[:, 9] = material
        vertices[:, 12] = self.seed
        a = np.arange(segments, dtype=np.uint32)
        sides = np.stack([a, a + 1, a + 1 + ring, a, a + 1 + ring, a + ring], axis=-1).reshape(-1)
        self._add(vertices, sides)
        self.disc(x, y, radius, z1, top or color, material if top is None else PLAIN, segments)

    def disc(
        self, x: float, y: float, radius: float, z: float, color: Color, material: int, segments: int = 14
    ) -> None:
        angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)
        vertices = np.zeros((segments + 1, 14), dtype=np.float32)
        vertices[0, 0:3] = (x, y, z)
        vertices[1:, 0] = x + radius * np.cos(angles)
        vertices[1:, 1] = y + radius * np.sin(angles)
        vertices[1:, 2] = z
        vertices[:, 5] = 1.0
        vertices[:, 6:9] = color
        vertices[:, 9] = material
        vertices[:, 12] = self.seed
        a = np.arange(1, segments + 1, dtype=np.uint32)
        self._add(vertices, np.stack([np.zeros_like(a), a, a % segments + 1], axis=-1).reshape(-1))

    def ellipsoid(
        self,
        x: float,
        y: float,
        z: float,
        radii: tuple[float, float, float],
        color: Color,
        material: int,
        lower: float = -1.0,
        segments: int = 10,
        rings: int = 6,
    ) -> None:
        """A smooth-shaded ellipsoid (from `lower`, -1 for the whole, 0 for a dome, to its top)."""
        heights = np.linspace(math.asin(lower), math.pi / 2, rings + 1)
        angles = np.linspace(0, 2 * np.pi, segments + 1)
        elevation, around = np.meshgrid(heights, angles, indexing="ij")
        unit = np.stack(
            [np.cos(elevation) * np.cos(around), np.cos(elevation) * np.sin(around), np.sin(elevation)], axis=-1
        )
        vertices = np.zeros((rings + 1, segments + 1, 14), dtype=np.float32)
        vertices[..., 0:3] = unit * radii + (x, y, z)
        normals = unit / radii
        vertices[..., 3:6] = normals / np.linalg.norm(normals, axis=-1, keepdims=True)
        vertices[..., 6:9] = color
        vertices[..., 9] = material
        vertices[..., 12] = self.seed
        index = np.arange((rings + 1) * (segments + 1), dtype=np.uint32).reshape(rings + 1, segments + 1)
        a, b, c, d = index[:-1, :-1], index[:-1, 1:], index[1:, :-1], index[1:, 1:]
        self._add(vertices.reshape(-1, 14), np.stack([a, b, d, a, d, c], axis=-1).reshape(-1))

    def gabled(
        self,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        z0: float,
        eaves: float,
        ridge: float,
        walls: Color,
        roof: Color,
        material: int,
    ) -> None:
        """A house or barn: walls up to the eaves, a pitched roof with its ridge along the longer side."""
        self.box(x0, x1, y0, y1, z0, eaves, walls, material, top=walls)
        along_x = (x1 - x0) >= (y1 - y0)
        if along_x:
            middle = (y0 + y1) / 2
            rise, run = ridge - eaves, middle - y0
            slope = math.hypot(rise, run)
            self.quad(
                [(x0, y0, eaves), (x1, y0, eaves), (x1, middle, ridge), (x0, middle, ridge)],
                (0.0, -rise / slope, run / slope),
                roof,
                PLAIN,
            )
            self.quad(
                [(x0, y1, eaves), (x0, middle, ridge), (x1, middle, ridge), (x1, y1, eaves)],
                (0.0, rise / slope, run / slope),
                roof,
                PLAIN,
            )
            for end, normal in ((x0, -1.0), (x1, 1.0)):
                self._triangle([(end, y0, eaves), (end, y1, eaves), (end, middle, ridge)], (normal, 0.0, 0.0), walls)
        else:
            middle = (x0 + x1) / 2
            rise, run = ridge - eaves, middle - x0
            slope = math.hypot(rise, run)
            self.quad(
                [(x0, y0, eaves), (x0, y1, eaves), (middle, y1, ridge), (middle, y0, ridge)],
                (-rise / slope, 0.0, run / slope),
                roof,
                PLAIN,
            )
            self.quad(
                [(x1, y0, eaves), (middle, y0, ridge), (middle, y1, ridge), (x1, y1, eaves)],
                (rise / slope, 0.0, run / slope),
                roof,
                PLAIN,
            )
            for end, normal in ((y0, -1.0), (y1, 1.0)):
                self._triangle([(x0, end, eaves), (x1, end, eaves), (middle, end, ridge)], (0.0, normal, 0.0), walls)

    def _triangle(
        self, corners: list[tuple[float, float, float]], normal: tuple[float, float, float], color: Color
    ) -> None:
        vertices = np.zeros((3, 14), dtype=np.float32)
        vertices[:, 0:3] = corners
        vertices[:, 3:6] = normal
        vertices[:, 6:9] = color
        vertices[:, 12] = self.seed
        self._add(vertices, np.array([0, 1, 2], dtype=np.uint32))

    def face(self, corners: list[tuple[float, float, float]], color: Color, material: int) -> None:
        """A flat face of 3 or 4 corners (a roof's slope), its normal facing up."""
        a, b, c = (np.array(corner) for corner in corners[:3])
        normal = np.cross(b - a, c - a)
        normal /= np.linalg.norm(normal) or 1.0
        if normal[2] < 0:
            normal = -normal
        points = corners if len(corners) == 4 else [*corners, corners[2]]
        self.quad(points, (float(normal[0]), float(normal[1]), float(normal[2])), color, material)

    def ridge_roof(
        self,
        footprint: tuple[float, float, float, float],
        eaves: float,
        section: list[tuple[float, float]],
        walls: Color,
        roof: Color,
        material: int = PLAIN,
    ) -> None:
        """A roof along the footprint's longer side, from its cross-section: (share of the way across, height
        above the eaves) from one edge to the other; the two ends closed with the walls' color.
        """
        x0, x1, y0, y1 = footprint
        along_x = (x1 - x0) >= (y1 - y0)
        start, end, low, high = (x0, x1, y0, y1) if along_x else (y0, y1, x0, x1)  # along the ridge, then across
        points = [(low + (high - low) * share, eaves + rise) for share, rise in section]

        def point(along: float, across: float, z: float) -> tuple[float, float, float]:
            return (along, across, z) if along_x else (across, along, z)

        for (pa, za), (pb, zb) in itertools.pairwise(points):
            self.face(
                [point(start, pa, za), point(end, pa, za), point(end, pb, zb), point(start, pb, zb)], roof, material
            )
        middle = (low + high) / 2
        for at, direction in ((start, -1.0), (end, 1.0)):  # the ends: triangles fanning from the middle
            normal = (direction, 0.0, 0.0) if along_x else (0.0, direction, 0.0)
            for (pa, za), (pb, zb) in itertools.pairwise(points):
                bottom = point(at, middle, eaves)
                self.quad([point(at, pa, za), point(at, pb, zb), bottom, bottom], normal, walls, material)

    def lathe(
        self,
        x: float,
        y: float,
        profile: list[tuple[float, float]],
        color: Color,
        material: int,
        segments: int = 14,
        cap: Color | None = None,
    ) -> None:
        """A shape turned around the upright axis at (x, y): `profile` is (z, radius) from the bottom up, smooth
        shaded; `cap` closes its top with a disc of that color.
        """
        angles = np.linspace(0, 2 * np.pi, segments + 1)
        cos, sin = np.cos(angles), np.sin(angles)
        ring = segments + 1
        levels = len(profile)
        vertices = np.zeros((levels * ring, 14), dtype=np.float32)
        for level, (z, r) in enumerate(profile):
            below = profile[max(level - 1, 0)]
            above = profile[min(level + 1, levels - 1)]
            slope_z, slope_r = above[0] - below[0], above[1] - below[1]  # along the profile
            length = math.hypot(slope_z, slope_r) or 1.0
            out, up = slope_z / length, -slope_r / length  # the normal: across the profile, outwards
            part = vertices[level * ring : (level + 1) * ring]
            part[:, 0] = x + r * cos
            part[:, 1] = y + r * sin
            part[:, 2] = z
            part[:, 3] = out * cos
            part[:, 4] = out * sin
            part[:, 5] = up
            part[:, 10] = angles * r
            part[:, 11] = z - profile[0][0]
        vertices[:, 6:9] = color
        vertices[:, 9] = material
        vertices[:, 12] = self.seed
        a = np.arange(segments, dtype=np.uint32)
        bands = [
            np.stack([a, a + 1, a + 1 + ring, a, a + 1 + ring, a + ring], axis=-1).reshape(-1) + level * ring
            for level in range(levels - 1)
        ]
        self._add(vertices, np.concatenate(bands).astype(np.uint32))
        if cap is not None:
            top_z, top_r = profile[-1]
            if top_r > 0:
                self.disc(x, y, top_r, top_z, cap, PLAIN if material in (LIGHT,) else material, segments)

    def arrays(self) -> tuple[FloatArray, IndexArray]:
        if not self.vertices:
            return np.zeros((0, 14), dtype=np.float32), np.zeros(0, dtype=np.uint32)
        return np.concatenate(self.vertices), np.concatenate(self.indices)


def footprint(prop: Prop) -> tuple[float, float, float, float]:
    """(x0, x1, y0, y1): the prop's footprint."""
    return prop.x - prop.width / 2, prop.x + prop.width / 2, prop.y - prop.length / 2, prop.y + prop.length / 2


def radius(prop: Prop) -> float:
    """The biggest round thing that fits its footprint."""
    return min(prop.width, prop.length) / 2


def shade(color: Color, factor: float) -> Color:
    return (min(color[0] * factor, 1.0), min(color[1] * factor, 1.0), min(color[2] * factor, 1.0))


def varied(rng: random.Random, color: Color, amount: float = 0.08) -> Color:
    """The color a little lighter or darker: no two props quite the same."""
    return shade(color, 1.0 + rng.uniform(-amount, amount))
