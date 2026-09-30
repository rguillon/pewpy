"""Meshes of the props standing on the built-up grounds (settlement.py): buildings, tanks, stacks, trees...

Built in bulk with numpy as plain arrays (ground_shader.py turns them into Panda3D geometry). Every vertex has
14 floats: position (3), normal (3), color (red, green, blue, material) and texture data (4: along the wall,
up the wall, the prop's seed from 0 to 1, unused). The material tells the prop shader how to paint a face (see
MATERIALS); the wall coordinates, in world units, place the windows.

Props are built in ground coordinates (x right, y down the loop, z up towards the camera), then turned into a
strip's model space (x right, y away from the camera, z up the screen) by `strip_arrays`.
Independent from Panda3D.
"""

import math
import random
from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from pewpy.settlement import Prop

Color = tuple[float, float, float]
FloatArray = NDArray[np.float32]
IndexArray = NDArray[np.uint32]

# How the prop shader paints a face (the color's 4th number).
PLAIN, OFFICE, HOMES, FURNACE, LIGHT, FOLIAGE, METAL, ROOFING = range(8)

# Colors: the same range as the voxel grounds these replace (ground_look.py, models.py): muted greys with a tint.
BUILDING_WALLS: tuple[Color, ...] = (
    (0.17, 0.18, 0.23),
    (0.2, 0.17, 0.25),
    (0.15, 0.2, 0.22),
    (0.21, 0.21, 0.23),
    (0.23, 0.2, 0.18),
)
ROOFS: tuple[Color, ...] = ((0.22, 0.22, 0.25), (0.26, 0.23, 0.28), (0.2, 0.23, 0.25), (0.25, 0.25, 0.25))
ROOF_UNIT: Color = (0.3, 0.3, 0.31)
BEACON: Color = (0.9, 0.1, 0.06)
REFINERY_METALS: tuple[Color, ...] = ((0.32, 0.33, 0.35), (0.38, 0.34, 0.28), (0.29, 0.32, 0.32), (0.4, 0.4, 0.38))
PLANT_WALLS: Color = (0.16, 0.16, 0.18)
PLANT_ROOF: Color = (0.24, 0.24, 0.26)
STACK: Color = (0.27, 0.23, 0.2)
FLAME: Color = (0.9, 0.4, 0.08)
PIPE: Color = (0.3, 0.28, 0.25)
HOUSE_WALLS: Color = (0.3, 0.28, 0.24)
HOUSE_ROOFS: tuple[Color, ...] = ((0.3, 0.1, 0.07), (0.22, 0.12, 0.08), (0.18, 0.17, 0.18))
BARN_WALLS: Color = (0.22, 0.08, 0.06)
BARN_ROOF: Color = (0.2, 0.2, 0.22)
SILO: Color = (0.3, 0.3, 0.32)
TREES: tuple[Color, ...] = ((0.07, 0.17, 0.06), (0.05, 0.13, 0.05), (0.09, 0.15, 0.05))
HEDGE: Color = (0.04, 0.1, 0.04)
PALM_FRONDS: Color = (0.08, 0.2, 0.07)
PALM_TRUNK: Color = (0.2, 0.14, 0.08)
DEAD_WOOD: Color = (0.2, 0.17, 0.14)
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

    def arrays(self) -> tuple[FloatArray, IndexArray]:
        if not self.vertices:
            return np.zeros((0, 14), dtype=np.float32), np.zeros(0, dtype=np.uint32)
        return np.concatenate(self.vertices), np.concatenate(self.indices)


def build(mesh: PropMesh, prop: Prop) -> None:
    """Add a prop to a mesh."""
    rng = random.Random(prop.seed)  # noqa: S311 - looks, not cryptography
    mesh.seed = (prop.seed % 997) / 997
    BUILDERS[prop.kind](mesh, rng, prop)


def _footprint(prop: Prop) -> tuple[float, float, float, float]:
    return prop.x - prop.width / 2, prop.x + prop.width / 2, prop.y - prop.length / 2, prop.y + prop.length / 2


def _radius(prop: Prop) -> float:
    return min(prop.width, prop.length) / 2


def _house(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    x0, x1, y0, y1 = _footprint(prop)
    eaves, ridge = prop.base + prop.height * 0.6, prop.base + prop.height
    mesh.gabled(x0, x1, y0, y1, prop.base, eaves, ridge, HOUSE_WALLS, rng.choice(HOUSE_ROOFS), HOMES)


def _barn(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    x0, x1, y0, y1 = _footprint(prop)
    eaves, ridge = prop.base + prop.height * 0.55, prop.base + prop.height
    mesh.gabled(x0, x1, y0, y1, prop.base, eaves, ridge, BARN_WALLS, BARN_ROOF, PLAIN)


def _silo(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    radius, top = _radius(prop), prop.base + prop.height
    mesh.cylinder(prop.x, prop.y, radius, prop.base, top, SILO, METAL)
    mesh.ellipsoid(prop.x, prop.y, top, (radius, radius, radius * 0.7), SILO, METAL, lower=0.0)


def _tank(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    radius, top = _radius(prop), prop.base + prop.height
    metal = rng.choice(REFINERY_METALS)
    mesh.cylinder(prop.x, prop.y, radius, prop.base, top, metal, METAL, segments=20)
    lid = (metal[0] * 1.15, metal[1] * 1.15, metal[2] * 1.15)
    mesh.ellipsoid(prop.x, prop.y, top, (radius, radius, radius * 0.12), lid, METAL, lower=0.0, segments=20, rings=3)


def _plant(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    x0, x1, y0, y1 = _footprint(prop)
    top = prop.base + prop.height
    mesh.box(x0, x1, y0, y1, prop.base, top, PLANT_WALLS, FURNACE, top=PLANT_ROOF, top_material=ROOFING)
    for _ in range(rng.randint(1, 2)):  # small chimneys
        cx, cy = rng.uniform(x0 + 0.015, x1 - 0.015), rng.uniform(y0 + 0.015, y1 - 0.015)
        mesh.cylinder(cx, cy, 0.007, top, top + rng.uniform(0.03, 0.06), STACK, PLAIN, segments=8)


def _stack(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    radius, top = _radius(prop), prop.base + prop.height
    mesh.cylinder(prop.x, prop.y, radius * 0.6, prop.base, top, STACK, PLAIN, segments=12)
    flame = (radius * 0.8, radius * 0.8, radius * 1.6)
    mesh.ellipsoid(prop.x, prop.y, top + radius * 0.7, flame, FLAME, LIGHT, segments=8, rings=4)


def _tree(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    # Seen from above, a crown is all that shows (no trunk, no underside): a few sides and rings are plenty, and
    # there can be hundreds of trees on screen.
    crown = (prop.width / 2, prop.length / 2, prop.height * 0.45)
    middle = prop.base + prop.height * 0.55
    mesh.ellipsoid(prop.x, prop.y, middle, crown, rng.choice(TREES), FOLIAGE, lower=-0.5, segments=7, rings=3)


def _hedge(mesh: PropMesh, rng: random.Random, prop: Prop) -> None:
    x0, x1, y0, y1 = _footprint(prop)
    mesh.box(x0, x1, y0, y1, prop.base, prop.base + prop.height, HEDGE, FOLIAGE)


def _building(
    mesh: PropMesh, rng: random.Random, footprint: tuple[float, float, float, float], z0: float, height: float
) -> None:
    x0, x1, y0, y1 = footprint
    walls = rng.choice(BUILDING_WALLS)
    roof = rng.choice(ROOFS)
    material = OFFICE if height > 0.12 or rng.random() < 0.5 else HOMES
    top = z0 + height
    if height > 0.25 and min(x1 - x0, y1 - y0) > 0.07:  # a tower: a setback, and its upper part narrower
        waist = z0 + height * rng.uniform(0.55, 0.8)
        mesh.box(x0, x1, y0, y1, z0, waist, walls, material, top=roof, top_material=ROOFING)
        inset = min(x1 - x0, y1 - y0) * rng.uniform(0.12, 0.25)
        x0, x1, y0, y1 = x0 + inset, x1 - inset, y0 + inset, y1 - inset
        mesh.box(x0, x1, y0, y1, waist, top, walls, material, top=roof, top_material=ROOFING)
        mesh.box(x0, x0 + 0.006, y0, y0 + 0.006, top, top + 0.006, BEACON, LIGHT)  # a red light on a corner
    else:
        mesh.box(x0, x1, y0, y1, z0, top, walls, material, top=roof, top_material=ROOFING)
    for _ in range(rng.randint(0, 3)):  # machinery on the roof
        size = rng.uniform(0.008, 0.018)
        cx, cy = rng.uniform(x0 + size, x1 - size), rng.uniform(y0 + size, y1 - size)
        if x1 - x0 > 2 * size and y1 - y0 > 2 * size:
            mesh.box(
                cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2, top, top + size * 0.6, ROOF_UNIT, PLAIN
            )


def _palm(mesh: PropMesh, rng: random.Random, x: float, y: float, z0: float, height: float, reach: float) -> None:
    """A thin trunk and a star of drooping fronds."""
    top = z0 + height
    mesh.box(x - 0.0015, x + 0.0015, y - 0.0015, y + 0.0015, z0, top, PALM_TRUNK, PLAIN)
    turn = rng.uniform(0, 2 * math.pi)
    for index in range(6):
        angle = turn + index * math.pi / 3
        along = (math.cos(angle), math.sin(angle))
        side = (-along[1] * 0.006, along[0] * 0.006)
        tip = (x + along[0] * reach, y + along[1] * reach, top - height * 0.25)
        corners = [
            (x - side[0], y - side[1], top),
            (x + side[0], y + side[1], top),
            (tip[0], tip[1], tip[2]),
            (tip[0], tip[1], tip[2]),
        ]
        mesh.quad(corners, (along[0] * 0.3, along[1] * 0.3, 1.0), PALM_FRONDS, FOLIAGE)


def _dead_tree(mesh: PropMesh, rng: random.Random, x: float, y: float, z0: float, height: float) -> None:
    """A bare grey trunk with a couple of broken branches."""
    mesh.box(x - 0.002, x + 0.002, y - 0.002, y + 0.002, z0, z0 + height, DEAD_WOOD, PLAIN)
    for _ in range(rng.randint(1, 3)):
        z = z0 + height * rng.uniform(0.45, 0.85)
        length = rng.uniform(0.008, 0.016) * rng.choice((-1, 1))
        if rng.random() < 0.5:
            mesh.box(min(x, x + length), max(x, x + length), y - 0.0012, y + 0.0012, z, z + 0.0025, DEAD_WOOD, PLAIN)
        else:
            mesh.box(x - 0.0012, x + 0.0012, min(y, y + length), max(y, y + length), z, z + 0.0025, DEAD_WOOD, PLAIN)


def _pipes(mesh: PropMesh, footprint: tuple[float, float, float, float], z0: float, height: float) -> None:
    x0, x1, y0, y1 = footprint
    along_y = (y1 - y0) > (x1 - x0)
    length = (y1 - y0) if along_y else (x1 - x0)
    across = (x0, x1) if along_y else (y0, y1)
    count = 4
    for index in range(count):
        offset = across[0] + (across[1] - across[0]) * (index + 0.5) / count
        radius = 0.004 + 0.002 * (index % 2)
        z = z0 + height
        # A pipe lying along the rack: a cylinder built upright, then turned over by swapping axes.
        start = len(mesh.vertices)
        mesh.cylinder(0.0, 0.0, radius, 0.0, length, PIPE, METAL, segments=8)
        for vertices in mesh.vertices[start:]:
            px, py, pz = vertices[:, 0].copy(), vertices[:, 1].copy(), vertices[:, 2].copy()
            nx, ny, nz = vertices[:, 3].copy(), vertices[:, 4].copy(), vertices[:, 5].copy()
            if along_y:
                vertices[:, 0], vertices[:, 1], vertices[:, 2] = offset + px, y0 + pz, z + py
                vertices[:, 3], vertices[:, 4], vertices[:, 5] = nx, nz, ny
            else:
                vertices[:, 0], vertices[:, 1], vertices[:, 2] = x0 + pz, offset + px, z + py
                vertices[:, 3], vertices[:, 4], vertices[:, 5] = nz, nx, ny
    step = 0.06
    for index in range(int(length / step) + 1):  # supports
        at = index * step
        if along_y:
            mesh.box(x0, x1, y0 + at, y0 + at + 0.004, z0, z0 + height, PIPE, PLAIN)
        else:
            mesh.box(x0 + at, x0 + at + 0.004, y0, y1, z0, z0 + height, PIPE, PLAIN)


BUILDERS: dict[str, Callable[[PropMesh, random.Random, Prop], None]] = {
    "building": lambda mesh, rng, prop: _building(mesh, rng, _footprint(prop), prop.base, prop.height),
    "house": _house,
    "barn": _barn,
    "silo": _silo,
    "tank": _tank,
    "plant": _plant,
    "stack": _stack,
    "pipes": lambda mesh, rng, prop: _pipes(mesh, _footprint(prop), prop.base, prop.height),
    "tree": _tree,
    "palm": lambda mesh, rng, prop: _palm(mesh, rng, prop.x, prop.y, prop.base, prop.height, prop.width / 2),
    "dead_tree": lambda mesh, rng, prop: _dead_tree(mesh, rng, prop.x, prop.y, prop.base, prop.height),
    "hedge": _hedge,
}


def strip_arrays(props: list[Prop], first_y: float) -> tuple[FloatArray, IndexArray]:
    """Every prop of a strip, in the strip's model space: x right, y away from the camera (heights towards the
    camera are -y), z up the screen from the strip's top edge (`first_y` down the loop)."""
    mesh = PropMesh()
    for prop in props:
        build(mesh, prop)
    vertices, indices = mesh.arrays()
    model = vertices.copy()
    model[:, 1] = -vertices[:, 2]
    model[:, 2] = -(vertices[:, 1] - first_y)
    model[:, 4] = -vertices[:, 5]
    model[:, 5] = -vertices[:, 4]
    return model, indices
