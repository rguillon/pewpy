"""The colors of each kind of ground (terrain.py BIOMES), and building a strip of it for Panda3D.

A painter turns a strip's heights and kinds into colored voxels, plus which voxels shine: "glow" ones as a lit
pane (windows), "burn" ones all over (lava, flames). Everything stays dark and muted so bullets stand out.
"""

from collections.abc import Callable

from panda3d.core import NodePath, Vec3

from pewpy.graphics.models import (
    DEEP_WATER,
    Cell,
    Color,
    MeshBuilder,
    buried,
    city_cells,
    ground_cells,
    island_cells,
    mottle,
    shade,
    water_surface,
)
from pewpy.scenery.terrain import BIOMES, TOWN_LIGHT, Kind

Cells = tuple[dict[Cell, Color], frozenset[Cell], frozenset[Cell]]  # (colors, glowing, burning)
Painter = Callable[[list[list[int]], list[list[int]], int], Cells]  # (heights, kinds, max height) -> Cells
# (kind, level, column height, max height, column, row) -> (color, mode: "" / "glow" / "burn")
Paint = Callable[[int, int, int, int, int, int], tuple[Color, str]]

WATER_COLORS: dict[str, Color] = {
    "desert": (0.03, 0.1, 0.1, 1),
    "forest": (0.02, 0.06, 0.06, 1),
    "canyon": (0.03, 0.08, 0.08, 1),
    "pack_ice": (0.01, 0.025, 0.05, 1),
    "swamp": (0.015, 0.045, 0.04, 1),
}


def levels(height: int, water: bool) -> range:
    """The voxels of a column: none below 0 (a gap), none at water level, else from the base layer up."""
    if height < 0:
        return range(0)
    return range(1 if water else 0, height + 1)


def painter(paint: Paint, water: bool) -> Painter:
    def cells(heights: list[list[int]], kinds: list[list[int]], max_height: int) -> Cells:
        colors: dict[Cell, Color] = {}
        glowing, burning = set(), set()
        for row, (line, line_kinds) in enumerate(zip(heights, kinds, strict=True)):
            for column, (height, kind) in enumerate(zip(line, line_kinds, strict=True)):
                for level in levels(height, water):
                    cell = (column, row, -level)
                    color, mode = paint(kind, level, height, max_height, column, row)
                    colors[cell] = color if mode else mottle(color, cell)
                    if mode == "glow":
                        glowing.add(cell)
                    elif mode == "burn":
                        burning.add(cell)
        return colors, frozenset(glowing), frozenset(burning)

    return cells


def _stripes(color: Color, row: int, strength: float = 0.15) -> Color:
    """Crop rows: every other row a bit darker."""
    return shade(color, 1 - strength * (row % 2))


def _share(level: int, max_height: int) -> float:
    return level / max(max_height, 1)


def _desert(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    top = level == height
    if kind == Kind.ROCK:
        band = ((0.3, 0.17, 0.11, 1), (0.24, 0.14, 0.1, 1))[(level // 2) % 2]
        return ((0.34, 0.22, 0.14, 1) if top else band), ""
    if kind == Kind.PALM:
        return ((0.08, 0.2, 0.07, 1) if top else (0.2, 0.14, 0.08, 1)), ""
    if kind == Kind.GRASS:
        return (0.12, 0.18, 0.08, 1), ""
    low, high = (0.24, 0.18, 0.11, 1), (0.34, 0.27, 0.16, 1)
    share = _share(level, max_height // 2)
    sand = tuple(a + (b - a) * min(share, 1.0) for a, b in zip(low, high, strict=True))
    return _stripes((sand[0], sand[1], sand[2], 1.0), row + level, 0.06), ""


TREE_COLORS = {
    Kind.TREE: (0.05, 0.14, 0.06, 1),
    Kind.TREE_DARK: (0.03, 0.09, 0.05, 1),
    Kind.TREE_LIGHT: (0.1, 0.17, 0.07, 1),
}


def _forest(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    if kind in TREE_COLORS:
        return shade(TREE_COLORS[Kind(kind)], 1.25 if level == height else 0.8), ""
    return (0.06, 0.1, 0.05, 1), ""


CANYON_BANDS: tuple[Color, ...] = (
    (0.3, 0.14, 0.09, 1),
    (0.36, 0.2, 0.12, 1),
    (0.26, 0.12, 0.08, 1),
    (0.4, 0.27, 0.17, 1),
)


def _canyon(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    if kind == Kind.SAND:
        return (0.33, 0.27, 0.18, 1), ""
    if kind == Kind.GRASS:
        return (0.12, 0.15, 0.07, 1), ""
    if level == height and height >= max_height * 0.7:
        return (0.32, 0.22, 0.13, 1), ""  # the plateau
    return CANYON_BANDS[(level // 2) % len(CANYON_BANDS)], ""  # rock layers


FARM_COLORS: dict[int, Color] = {
    Kind.ROAD: (0.17, 0.13, 0.09, 1),
    Kind.WHEAT: (0.36, 0.3, 0.12, 1),
    Kind.CROP: (0.1, 0.2, 0.07, 1),
    Kind.PLOWED: (0.16, 0.1, 0.06, 1),
    Kind.LAVENDER: (0.22, 0.15, 0.3, 1),
    Kind.GRASS: (0.1, 0.16, 0.07, 1),
    Kind.HEDGE: (0.04, 0.1, 0.04, 1),
    Kind.TREE: (0.07, 0.17, 0.06, 1),
}


def _farmland(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    top = level == height
    if kind == Kind.HOUSE:
        return ((0.3, 0.1, 0.07, 1) if top else (0.3, 0.28, 0.24, 1)), ""
    if kind == Kind.SILO:
        return ((0.35, 0.35, 0.38, 1) if top else (0.3, 0.3, 0.32, 1)), ""
    color = FARM_COLORS.get(kind, FARM_COLORS[Kind.GRASS])
    if kind in (Kind.WHEAT, Kind.CROP, Kind.PLOWED, Kind.LAVENDER):
        return _stripes(color, row, 0.3 if kind == Kind.PLOWED else 0.15), ""
    return color, ""


def _pack_ice(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    top = level == height
    if kind == Kind.BERG:
        return ((0.4, 0.47, 0.53, 1) if top else (0.24, 0.33, 0.42, 1)), ""
    return ((0.32, 0.36, 0.4, 1) if top else (0.2, 0.25, 0.3, 1)), ""


def _volcano(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    if kind == Kind.LAVA:
        return (0.48, 0.12, 0.02, 1), "burn"  # redder and dimmer than the yellow player bullets
    if kind == Kind.EMBER and level == height:
        return (0.3, 0.07, 0.02, 1), "burn"
    return ((0.1, 0.09, 0.09, 1) if _share(level, max_height) > 0.6 else (0.06, 0.055, 0.06, 1)), ""  # ash on top


def _swamp(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    if kind == Kind.DEAD_TREE:
        return (0.2, 0.17, 0.14, 1), ""
    if kind == Kind.REED:
        return ((0.2, 0.22, 0.09, 1) if level == height else (0.14, 0.16, 0.07, 1)), ""
    return (0.15, 0.13, 0.08, 1), ""  # mud, lighter than the water around it


def _clouds(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    low, high = (0.2, 0.23, 0.32), (0.33, 0.37, 0.47)  # moonlit: cool blue-grey, well below the bullets
    share = min(1.0, _share(level, max_height) + (0.35 if level == height else 0.0))  # lit tops
    red, green, blue = (a + (b - a) * share for a, b in zip(low, high, strict=True))
    return (red, green, blue, 1.0), ""


TOWN_LIGHT_COLORS: tuple[Color, ...] = ((0.45, 0.32, 0.12, 1), (0.3, 0.4, 0.45, 1))  # dim amber, pale blue
TOWN_LIGHT_DEPTH = 14  # voxels below the clouds' base: far enough to drift slower than the clouds


def _cloud_deck(heights: list[list[int]], kinds: list[list[int]], max_height: int) -> Cells:
    """Clouds, plus a few town lights on the ground far below, seen through the gaps."""
    colors, glowing, burning = painter(_clouds, water=False)(heights, kinds, max_height)
    lights = set()
    for row, line in enumerate(heights):
        for column, height in enumerate(line):
            if height == TOWN_LIGHT:
                cell = (column, row, TOWN_LIGHT_DEPTH)
                colors[cell] = TOWN_LIGHT_COLORS[(column + row) % len(TOWN_LIGHT_COLORS)]
                lights.add(cell)
    return colors, glowing | lights, burning


REFINERY_METALS: tuple[Color, ...] = ((0.2, 0.21, 0.22, 1), (0.25, 0.22, 0.18, 1), (0.18, 0.2, 0.2, 1))


def _refinery(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    lot, what = divmod(kind, 100)
    top = level == height
    if what == Kind.ROAD:
        return ((0.4, 0.28, 0.08, 1), "glow") if _hash(column, row) < 0.03 else ((0.04, 0.04, 0.045, 1), "")
    if what == Kind.YARD:
        return (0.06, 0.065, 0.07, 1), ""
    if what == Kind.PIPE:
        return (0.22, 0.2, 0.18, 1), ""
    if what == Kind.TANK:
        metal = REFINERY_METALS[lot % len(REFINERY_METALS)]
        return (shade(metal, 1.3) if top else metal), ""
    if what == Kind.STACK:
        return ((0.7, 0.3, 0.05, 1), "burn") if top else ((0.18, 0.14, 0.12, 1), "")
    # a plant: dark walls, rows of glowing furnace windows, a roof
    if top:
        return (0.15, 0.15, 0.16, 1), ""
    if level % 2 == 1 and _hash(column + lot, row + level) < 0.3:
        return (0.5, 0.25, 0.06, 1), "glow"
    return (0.1, 0.1, 0.11, 1), ""


def _mountains(kind: int, level: int, height: int, max_height: int, column: int, row: int) -> tuple[Color, str]:
    if kind == Kind.ICE:
        return (0.4, 0.46, 0.52, 1), ""
    share = _share(level, max_height)
    if share > 0.7:
        return (0.5, 0.52, 0.56, 1), ""  # snow
    if share < 0.3:
        return (0.05, 0.1, 0.06, 1), ""  # pine forest
    return ((0.2, 0.2, 0.22, 1) if (level // 2) % 2 else (0.17, 0.17, 0.19, 1)), ""  # rock


def _hash(a: int, b: int) -> float:
    return ((a * 73856093) ^ (b * 19349663)) % 10007 / 10007


def _no_shine(cells: dict[Cell, Color]) -> Cells:
    return cells, frozenset(), frozenset()


PAINTERS: dict[str, Painter] = {
    "planet": lambda heights, kinds, max_height: _no_shine(ground_cells(heights, 0, max_height)),
    "city": lambda heights, kinds, max_height: (*city_cells(heights, kinds, max_height), frozenset()),
    "ocean": lambda heights, kinds, max_height: _no_shine(island_cells(heights, max_height)),
    "desert": painter(_desert, water=True),
    "forest": painter(_forest, water=True),
    "canyon": painter(_canyon, water=True),
    "farmland": painter(_farmland, water=False),
    "pack_ice": painter(_pack_ice, water=True),
    "volcano": painter(_volcano, water=False),
    "swamp": painter(_swamp, water=True),
    "clouds": _cloud_deck,
    "refinery": painter(_refinery, water=False),
    "mountains": painter(_mountains, water=False),
}


def ground_chunk_model(
    biome: str,
    heights: list[list[int]],
    kinds: list[list[int]],
    voxel: float,
    above: list[int],
    below: list[int],
    max_height: int,
    shallows: list[list[float]] | None = None,
) -> NodePath:
    """One strip of ground. The node's origin is its top-left corner, on the base layer.

    `above` and `below` are the heights of the neighboring rows (in the strips drawn before and after) so the
    seams between strips have no extra faces and are shaded like the rest. Voxels buried on all six sides aren't
    drawn, but still hide faces and shade corners. `shallows` (one more row than the strip) is for grounds with
    water: the water surface.
    """
    water = BIOMES[biome].water
    colors, glowing, burning = PAINTERS[biome](heights, kinds, max_height)

    def solid_rows(lines: list[list[int]], first: int) -> set[Cell]:
        return {
            (column, first + row, -level)
            for row, line in enumerate(lines)
            for column, height in enumerate(line)
            for level in levels(height, water)
        }

    solid = frozenset(set(colors) | solid_rows([above], -1) | solid_rows([below], len(heights)))
    exposed = {cell: color for cell, color in colors.items() if not buried(cell, solid)}
    mesh = MeshBuilder()
    mesh.cells(exposed, voxel, Vec3(voxel / 2, 0, -voxel / 2), solid, glowing, burning)
    if water and shallows is not None:
        water_surface(mesh, shallows, voxel, len(heights[0]), WATER_COLORS.get(biome, DEEP_WATER))
    return NodePath(mesh.build("ground"))
