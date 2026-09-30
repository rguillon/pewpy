from itertools import pairwise

import pytest

from pewpy import background, config
from pewpy.background import Area, Drifter, DriftLayer, Scenery, Starfield
from pewpy.terrain import (
    CITY_DEPTH,
    CITY_MAX_HEIGHT,
    GROUND_CHUNKS,
    GROUND_DEPTH,
    GROUND_MAX_HEIGHT,
    GROUND_SPEED,
    GROUND_VOXEL,
    ISLAND_MAX_HEIGHT,
    ISLAND_SHARE,
    SEA_DEPTH,
    Terrain,
)

AREA = Area(-1.0, 1.0, -1.2, 1.8)


class FakeView:
    """Farther layers cover more and seem to move slower, like through the real camera."""

    def area(self, depth: float) -> Area:
        return Area(-1.0 - 0.2 * depth, 1.0 + 0.2 * depth, -1.2, 1.8 + 0.5 * depth)

    def parallax(self, depth: float) -> float:
        return 1 / (1 + 0.2 * depth)


def test_star_layers_scroll_down_with_parallax():
    starfield = Starfield(seed=0, area=AREA)
    starfield.update(0.1, scroll_speed=0.2)
    for layer in starfield.layers:
        assert layer.offset == pytest.approx(0.2 * layer.speed_factor * 0.1)
    assert len({layer.speed_factor for layer in starfield.layers}) > 1


def test_star_layers_wrap_after_one_area_height():
    starfield = Starfield(seed=0, area=AREA)
    layer = starfield.layers[-1]
    starfield.update(AREA.height / layer.speed_factor + 0.5, scroll_speed=1.0)
    assert layer.offset == pytest.approx(0.5 * layer.speed_factor)


def test_stars_fill_the_area_and_stay_still_without_scrolling():
    starfield = Starfield(seed=0, area=AREA)
    stars = [star for layer in starfield.layers for star in layer.stars]
    assert all(AREA.left <= x <= AREA.right and AREA.bottom <= y <= AREA.top for x, y in stars)
    starfield.update(1.0, scroll_speed=0.0)
    assert all(layer.offset == 0 for layer in starfield.layers)


def test_drifters_move_spin_and_come_back_above_the_top():
    rock = Drifter(0.0, AREA.bottom - 0.09, size=0.1, speed_factor=0.5, spin=(10.0, 0.0, -20.0))
    layer = DriftLayer("rock", 1.0, AREA, [rock])
    layer.update(0.5, scroll_speed=0.2)
    assert rock.angle == pytest.approx((5.0, 0.0, -10.0))
    assert AREA.top - 0.2 < rock.y <= AREA.top + rock.size
    assert AREA.left <= rock.x <= AREA.right


def test_ground_chunks_follow_each_other_down_and_loop():
    terrain = Terrain(AREA, speed_factor=1.0, seed=0)
    tops = [terrain.chunk_top(chunk) for chunk in range(GROUND_CHUNKS)]
    for upper, lower in pairwise(tops):
        assert upper - lower == pytest.approx(terrain.chunk_height)
    terrain.update(1.0, scroll_speed=0.1)
    assert terrain.chunk_top(0) == pytest.approx(tops[0] - 0.1)
    terrain.update(terrain.loop_length / 0.1 - 1.0, scroll_speed=0.1)  # one full loop in total
    assert terrain.chunk_top(0) == pytest.approx(tops[0])


def test_ground_always_covers_the_screen():
    terrain = Terrain(AREA, speed_factor=1.0, seed=0)
    for _ in range(50):
        terrain.update(0.37, scroll_speed=0.5)
        spans = sorted((top - terrain.chunk_height, top) for top in map(terrain.chunk_top, range(GROUND_CHUNKS)))
        covered_to = AREA.bottom
        for bottom, top in spans:
            if bottom <= covered_to + 1e-9:
                covered_to = max(covered_to, top)
        assert covered_to >= AREA.top


def test_ground_heights_stay_in_range_and_cover_the_width():
    terrain = Terrain(AREA, speed_factor=1.0, seed=3)
    assert len(terrain.heights) == terrain.rows
    assert all(len(row) == terrain.columns for row in terrain.heights)
    assert {height for row in terrain.heights for height in row} <= set(range(GROUND_MAX_HEIGHT + 1))
    assert len({height for row in terrain.heights for height in row}) > 1  # not flat
    assert terrain.columns * terrain.voxel >= AREA.width
    assert terrain.left == pytest.approx(-terrain.columns * terrain.voxel / 2)


def test_smaller_ground_voxels_make_the_same_landscape_finer():
    default = Terrain(AREA, speed_factor=1.0, seed=0)
    fine = Terrain(AREA, speed_factor=1.0, seed=0, voxel=GROUND_VOXEL / 4)
    assert fine.chunk_rows_count == 4 * default.chunk_rows_count
    assert fine.max_height == 4 * default.max_height
    assert fine.chunk_height == pytest.approx(default.chunk_height)  # same size in the world
    assert fine.loop_length == pytest.approx(default.loop_length)
    assert max(max(row) for row in fine.heights) <= fine.max_height
    assert max(max(row) for row in fine.heights) > default.max_height  # hills keep their height in the world


def test_ground_loop_grows_to_stay_longer_than_the_screen():
    tall = Area(-1, 1, -10, 10)
    terrain = Terrain(tall, speed_factor=1.0)
    assert terrain.chunks > GROUND_CHUNKS
    assert terrain.loop_length >= tall.height + terrain.chunk_height


def make_city(seed: int = 0) -> Terrain:
    return Terrain(AREA, speed_factor=1.0, seed=seed, voxel=0.04, biome="city")


def test_city_has_streets_and_buildings_of_one_height_each():
    city = make_city()
    heights_by_lot: dict[int, set[int]] = {}
    for line, line_lots in zip(city.heights, city.kinds, strict=True):
        for height, lot in zip(line, line_lots, strict=True):
            heights_by_lot.setdefault(lot, set()).add(height)
    assert heights_by_lot[0] == {0}  # streets are flat
    assert all(len(heights) == 1 for lot, heights in heights_by_lot.items() if lot)  # one height per building
    tallest = max(max(line) for line in city.heights)
    assert tallest <= city.max_height == round(CITY_MAX_HEIGHT / 0.04)
    assert tallest > city.max_height // 2  # some towers
    assert len(heights_by_lot) > 20


def test_city_street_grid_loops():
    city = make_city()
    # A street runs along the top of the first block, so the loop's first row (just below its last) is street.
    assert set(city.kinds[0]) == {0}
    assert city.chunk_kinds(0) == city.kinds[: city.chunk_rows_count]


def make_islands(seed: int = 0) -> Terrain:
    return Terrain(AREA, speed_factor=1.0, seed=seed, voxel=0.04, biome="ocean")


@pytest.mark.parametrize("seed", range(4))
def test_islands_cover_the_same_share_of_the_sea_whatever_the_seed(seed):
    sea = make_islands(seed)
    land = sum(height > 0 for line in sea.heights for height in line) / (sea.rows * sea.columns)
    assert land == pytest.approx(ISLAND_SHARE, abs=0.01)
    assert max(max(line) for line in sea.heights) == sea.max_height == round(ISLAND_MAX_HEIGHT / 0.04)


def test_water_gets_shallower_near_the_islands():
    sea = make_islands()
    for line, shallow_line in zip(sea.heights, sea.shallows, strict=True):
        for height, shallow in zip(line, shallow_line, strict=True):
            assert 0.0 <= shallow <= 1.0
            if height > 0:
                assert shallow == 1.0
    next_to_land, open_sea = [], []
    for row in range(sea.rows):
        for column in range(1, sea.columns - 1):
            if sea.heights[row][column] == 0:
                beside = (sea.heights[row][column - 1], sea.heights[row][column + 1])
                (next_to_land if any(beside) else open_sea).append(sea.shallows[row][column])
    assert sum(next_to_land) / len(next_to_land) > sum(open_sea) / len(open_sea) + 0.3


def test_each_strip_of_sea_knows_the_next_strips_first_row():
    sea = make_islands()
    last = sea.chunks - 1
    shallows = sea.chunk_shallows(last)
    assert len(shallows) == sea.chunk_rows_count + 1
    assert shallows[-1] == sea.shallows[0]  # the loop wraps


def test_islands_stay_behind_the_ships():
    scenery = Scenery("ocean", FakeView(), seed=0, ground_voxel=0.04)
    assert scenery.terrain is not None
    assert scenery.terrain.biome == "ocean"
    assert scenery.terrain.depth == SEA_DEPTH
    assert SEA_DEPTH - ISLAND_MAX_HEIGHT > 0.1


def test_city_sits_deeper_than_the_hills():
    scenery = Scenery("city", FakeView(), seed=0, ground_voxel=0.04)
    assert scenery.terrain is not None
    assert scenery.terrain.biome == "city"
    assert scenery.terrain.depth == CITY_DEPTH > GROUND_DEPTH
    # Its tallest towers stay behind the ships (the play plane is at depth 0).
    assert CITY_DEPTH - CITY_MAX_HEIGHT > 0.1


@pytest.mark.parametrize(
    ("kind", "stars", "layers", "ground"),
    [
        ("space", True, ["cloud", "planet"], False),
        ("planet", False, [], True),
        ("city", False, [], True),
        ("ocean", False, [], True),
        ("debris", True, ["rock", "rock"], False),
    ],
)
def test_each_kind_of_background_has_its_own_scenery(kind, stars, layers, ground):
    scenery = Scenery(kind, FakeView(), seed=0)
    assert (scenery.starfield is not None) == stars
    assert [layer.kind for layer in scenery.layers] == layers
    assert (scenery.terrain is not None) == ground
    scenery.update(0.1, scroll_speed=0.2)  # doesn't fail


def test_ground_seems_to_move_at_ground_speed_on_screen():
    view = FakeView()
    terrain = Scenery("planet", view, seed=0).terrain
    assert terrain is not None
    on_screen = terrain.speed_factor * view.parallax(GROUND_DEPTH)
    assert on_screen == pytest.approx(GROUND_SPEED)


def test_ground_speed_is_away_from_every_enemy_speed_of_level_2():
    # Enemy speeds down the screen as fractions of level 2's scroll speed (0.25): parked Sniper, Gunship,
    # Turret, Drone, Weaver.
    for enemy in (0.0, 0.6, 1.0, 1.2, 1.4):
        assert abs(GROUND_SPEED - enemy) >= 0.25


def test_stars_fill_bigger_areas_with_more_stars():
    scenery = Scenery("space", FakeView(), seed=0)
    assert scenery.starfield is not None
    count = sum(len(layer.stars) for layer in scenery.starfield.layers)
    assert count > config.STAR_COUNT  # the layer is bigger than the play area


def test_unknown_background_is_rejected():
    with pytest.raises(ValueError, match="unknown background"):
        Scenery("jungle", FakeView())


def mist_layers(scenery: Scenery) -> list[DriftLayer]:
    return [layer for layer in scenery.layers if layer.kind == "mist"]


def test_see_through_clouds_come_with_the_amount_asked():
    assert mist_layers(Scenery("forest", FakeView(), seed=0)) == []  # none by default
    assert mist_layers(Scenery("space", FakeView(), seed=0, clouds=1.0)) == []  # only over grounds
    light = mist_layers(Scenery("forest", FakeView(), seed=0, clouds=0.2))
    heavy = mist_layers(Scenery("forest", FakeView(), seed=0, clouds=0.9))
    assert len(heavy) == len(background.MIST_LAYERS)
    assert sum(len(layer.drifters) for layer in heavy) > sum(len(layer.drifters) for layer in light) > 0


def test_clouds_float_between_the_ground_and_the_ships():
    scenery = Scenery("mountains", FakeView(), seed=0, clouds=1.0)
    assert scenery.terrain is not None
    for layer in mist_layers(scenery):
        assert 0 < layer.depth < scenery.terrain.depth


def test_wind_blows_clouds_around_the_sides():
    cloud = Drifter(AREA.right + 0.05, 0.0, size=0.1, speed_factor=0.0, wind=0.1)
    layer = DriftLayer("mist", 0.1, AREA, [cloud])
    layer.update(1.0, scroll_speed=0.0)
    assert AREA.left - cloud.size <= cloud.x < AREA.left + 0.1  # gone off the right, back on the left
