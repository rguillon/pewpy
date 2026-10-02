from itertools import pairwise

import pytest

from pewpy.scenery import params
from pewpy.scenery.background import Area, Drifter, DriftLayer, Scenery, Starfield, mist_depths
from pewpy.scenery.ground.terrain import CHUNKS, GROUND_SPEED, Terrain
from pewpy.scenery.params import SceneryError

AREA = Area(-1.0, 1.0, -1.2, 1.8)


def space_stars() -> params.Stars:
    stars = params.resolve("space").stars
    assert stars is not None
    return stars


STARS = space_stars()


def ground_depth(name: str) -> float:
    ground = params.resolve(name).ground
    assert ground is not None
    return ground.depth


def planet() -> Terrain:
    return Terrain(AREA, 1.0, params.resolve("planet"), seed=0)


class FakeView:
    """Farther layers cover more and seem to move slower, like through the real camera."""

    def area(self, depth: float) -> Area:
        return Area(-1.0 - 0.2 * depth, 1.0 + 0.2 * depth, -1.2, 1.8 + 0.5 * depth)

    def parallax(self, depth: float) -> float:
        return 1 / (1 + 0.2 * depth)


def test_star_layers_scroll_down_with_parallax():
    starfield = Starfield(STARS, seed=0, area=AREA)
    starfield.update(0.1, scroll_speed=0.2)
    for layer in starfield.layers:
        assert layer.offset == pytest.approx(0.2 * layer.speed_factor * 0.1)
    assert len({layer.speed_factor for layer in starfield.layers}) > 1


def test_star_layers_wrap_after_one_area_height():
    starfield = Starfield(STARS, seed=0, area=AREA)
    layer = starfield.layers[-1]
    starfield.update(AREA.height / layer.speed_factor + 0.5, scroll_speed=1.0)
    assert layer.offset == pytest.approx(0.5 * layer.speed_factor)


def test_stars_fill_the_area_and_stay_still_without_scrolling():
    starfield = Starfield(STARS, seed=0, area=AREA)
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
    terrain = planet()
    tops = [terrain.chunk_top(chunk) for chunk in range(CHUNKS)]
    for upper, lower in pairwise(tops):
        assert upper - lower == pytest.approx(terrain.chunk_height)
    terrain.update(1.0, scroll_speed=0.1)
    assert terrain.chunk_top(0) == pytest.approx(tops[0] - 0.1)
    terrain.update(terrain.loop_length / 0.1 - 1.0, scroll_speed=0.1)  # one full loop in total
    assert terrain.chunk_top(0) == pytest.approx(tops[0])


def test_ground_always_covers_the_screen():
    terrain = planet()
    for _ in range(50):
        terrain.update(0.37, scroll_speed=0.5)
        spans = sorted((top - terrain.chunk_height, top) for top in map(terrain.chunk_top, range(CHUNKS)))
        covered_to = AREA.bottom
        for bottom, top in spans:
            if bottom <= covered_to + 1e-9:
                covered_to = max(covered_to, top)
        assert covered_to >= AREA.top


def test_the_city_sits_deeper_than_the_hills():
    scenery = Scenery("city", FakeView(), seed=0)
    assert scenery.terrain is not None
    assert scenery.terrain.depth == ground_depth("city") > ground_depth("planet")


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
    on_screen = terrain.speed_factor * view.parallax(ground_depth("planet"))
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
    assert count > STARS.count  # the layer is bigger than the play area


def test_unknown_background_is_rejected():
    with pytest.raises(SceneryError, match="unknown background"):
        Scenery("jungle", FakeView())


def mist_layers(scenery: Scenery) -> list[DriftLayer]:
    return [layer for layer in scenery.layers if layer.kind == "mist"]


def test_see_through_clouds_come_with_the_amount_asked():
    assert mist_layers(Scenery("forest", FakeView(), seed=0)) == []  # none by default
    assert mist_layers(Scenery("space", FakeView(), seed=0, clouds=1.0)) == []  # only over grounds
    light = mist_layers(Scenery("forest", FakeView(), seed=0, clouds=0.2))
    heavy = mist_layers(Scenery("forest", FakeView(), seed=0, clouds=0.9))
    assert len(heavy) == len(params.resolve("forest").mist.layers)
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


def test_clouds_always_float_above_the_highest_ground():
    for name in params.backgrounds():
        scenery = params.resolve(name)
        if scenery.ground is None:
            assert mist_depths(scenery) == []
            continue
        top = scenery.ground.depth - scenery.ground.max_height  # the ground's closest point to the ships
        depths = mist_depths(scenery)
        assert all(depth <= top * 0.8 for depth in depths), name  # clearly above it, even the peaks
        layers = scenery.mist.layers
        assert all(depth <= layer.depth for depth, layer in zip(depths, layers, strict=True))
        assert all(depth > 0 for depth in depths)  # still behind the ships


def test_a_drifter_blown_off_the_left_comes_back_on_the_right():
    cloud = Drifter(AREA.left - 0.05, 0.0, size=0.1, speed_factor=0.0, wind=-0.1)
    DriftLayer("mist", 0.1, AREA, [cloud]).update(1.0, scroll_speed=0.0)
    assert AREA.right - 0.1 < cloud.x <= AREA.right + cloud.size
