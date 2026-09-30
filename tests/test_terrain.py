import pytest
from panda3d.core import GeomNode

from pewpy import ground_look
from pewpy.enemies import ENEMY_TYPES
from pewpy.level import load_levels
from pewpy.terrain import BIOMES, TOWN_LIGHT, Area, Kind, Terrain

AREA = Area(-1.0, 1.0, -1.2, 1.8)
ALL_BIOMES = sorted(BIOMES)


def make(biome: str, seed: int = 0) -> Terrain:
    return Terrain(AREA, speed_factor=1.0, seed=seed, voxel=0.04, biome=biome)


@pytest.mark.parametrize("biome", ALL_BIOMES)
def test_every_ground_fills_its_loop_with_sensible_columns(biome):
    ground = make(biome)
    assert len(ground.heights) == len(ground.kinds) == len(ground.shallows) == ground.rows
    assert all(len(line) == ground.columns for line in ground.heights)
    heights = {height for line in ground.heights for height in line}
    lowest = TOWN_LIGHT if biome == "clouds" else 0
    assert lowest <= min(heights) and max(heights) <= ground.max_height + 1
    assert len(heights) > 2  # not flat
    assert all(0.0 <= shallow <= 1.0 for line in ground.shallows for shallow in line)


@pytest.mark.parametrize("biome", ALL_BIOMES)
def test_every_ground_stays_behind_the_ships(biome):
    settings = BIOMES[biome]
    assert settings.depth - settings.max_height > 0.1  # the ships fly at depth 0 and are about 0.1 deep


@pytest.mark.parametrize("biome", [name for name in ALL_BIOMES if BIOMES[name].water])
def test_grounds_with_water_have_both_water_and_land(biome):
    ground = make(biome)
    water = sum(height == 0 for line in ground.heights for height in line) / (ground.rows * ground.columns)
    assert 0.002 < water < 0.9  # the desert only has a few oasis pools


@pytest.mark.parametrize("biome", ALL_BIOMES)
def test_every_ground_has_colors_and_the_shining_voxels_are_among_them(biome):
    ground = make(biome)
    colors, glowing, burning = ground_look.PAINTERS[biome](
        ground.chunk_rows(0), ground.chunk_kinds(0), ground.max_height
    )
    assert colors
    assert glowing <= set(colors) and burning <= set(colors)
    assert all(0.0 <= channel <= 1.0 for color in colors.values() for channel in color)


def test_lava_and_flames_burn():
    volcano = make("volcano")
    assert any(kind == Kind.LAVA for line in volcano.kinds for kind in line)
    _, _, burning = ground_look.PAINTERS["volcano"](volcano.heights, volcano.kinds, volcano.max_height)
    assert burning


def test_clouds_have_gaps_with_a_few_lights_far_below():
    clouds = make("clouds")
    heights = [height for line in clouds.heights for height in line]
    assert -1 in heights and TOWN_LIGHT in heights
    _, glowing, _ = ground_look.PAINTERS["clouds"](clouds.heights, clouds.kinds, clouds.max_height)
    assert any(layer == ground_look.TOWN_LIGHT_DEPTH for _, _, layer in glowing)


def test_farmland_has_fields_farms_and_roads():
    farmland = make("farmland", seed=3)
    kinds = {kind for line in farmland.kinds for kind in line}
    assert {Kind.ROAD, Kind.WHEAT, Kind.HOUSE} <= kinds


def test_a_ground_strip_builds_for_every_biome():
    for biome in ALL_BIOMES:
        ground = make(biome)
        shallows = ground.chunk_shallows(0) if ground.water else None
        node = ground_look.ground_chunk_model(
            biome, ground.chunk_rows(0), ground.chunk_kinds(0), ground.voxel, ground.heights[-1],
            ground.heights[ground.chunk_rows_count], ground.max_height, shallows,
        )  # fmt: skip
        geom_node = node.node()
        assert isinstance(geom_node, GeomNode)
        assert geom_node.getNumGeoms() == 1


def test_every_ground_has_levels():
    assert set(BIOMES) <= {level.background for level in load_levels()}


def test_no_ground_enemies_over_water_or_clouds():
    # Turrets, tanks and the like are on the ground: they would look odd on the sea, the ice floes or the clouds.
    for level in load_levels():
        if level.background in ("pack_ice", "swamp", "clouds", "ocean"):
            ground = [
                wave.enemy for wave in level.waves if wave.enemy in ENEMY_TYPES and ENEMY_TYPES[wave.enemy].ground
            ]
            assert ground == [], level.name


@pytest.mark.parametrize("biome", ALL_BIOMES)
def test_every_ground_builds_whatever_its_layout(biome):
    """Features placed near the ground's edges (a refinery's stacks in small yards) stay inside it."""
    for seed in range(10):
        for voxel in (0.04, 0.07):
            terrain = Terrain(AREA, speed_factor=1.0, seed=seed, voxel=voxel, biome=biome)
            assert len(terrain.heights) == terrain.rows
