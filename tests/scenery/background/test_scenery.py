import pytest

from pewpy.scenery import params
from pewpy.scenery.background.drift import DriftLayer
from pewpy.scenery.background.scenery import Scenery, mist_depths
from pewpy.scenery.ground.terrain import GROUND_SPEED
from pewpy.scenery.params import SceneryError
from tests.scenery.background.views import FakeView


def ground_depth(name: str) -> float:
    ground = params.resolve(name).ground
    assert ground is not None
    return ground.depth


def test_the_city_sits_deeper_than_the_savanna() -> None:
    scenery = Scenery("city", FakeView(), seed=0)
    assert scenery.terrain is not None
    assert scenery.terrain.depth == ground_depth("city") > ground_depth("savanna")


@pytest.mark.parametrize(
    ("kind", "stars", "layers", "ground"),
    [
        ("space", True, ["cloud", "planet"], False),
        ("savanna", False, [], True),
        ("city", False, [], True),
        ("salt_pan", False, [], True),
    ],
)
def test_each_kind_of_background_has_its_own_scenery(kind: str, stars: bool, layers: list[str], ground: bool) -> None:
    scenery = Scenery(kind, FakeView(), seed=0)
    assert scenery.kind == kind
    assert (scenery.starfield is not None) == stars
    assert [layer.kind for layer in scenery.layers] == layers
    assert (scenery.terrain is not None) == ground
    scenery.update(0.1, scroll_speed=0.2)  # doesn't fail


def test_a_scenery_can_be_given_as_its_parameters() -> None:
    assert Scenery(params.resolve("forest"), FakeView(), seed=0).kind == "forest"


def test_ground_seems_to_move_at_ground_speed_on_screen() -> None:
    view = FakeView()
    terrain = Scenery("savanna", view, seed=0).terrain
    assert terrain is not None
    on_screen = terrain.speed_factor * view.parallax(ground_depth("savanna"))
    assert on_screen == pytest.approx(GROUND_SPEED)


def test_ground_speed_is_away_from_every_enemy_speed_of_level_2() -> None:
    # Enemy speeds down the screen as fractions of level 2's scroll speed (0.25): parked Sniper, Gunship,
    # Turret, Drone, Weaver.
    for enemy in (0.0, 0.6, 1.0, 1.2, 1.4):
        assert abs(GROUND_SPEED - enemy) >= 0.25


def test_stars_fill_bigger_areas_with_more_stars() -> None:
    scenery = Scenery("space", FakeView(), seed=0)
    assert scenery.starfield is not None
    count = sum(len(layer.stars) for layer in scenery.starfield.layers)
    stars = params.resolve("space").stars
    assert stars is not None
    assert count > stars.count  # the layer is bigger than the play area


def test_unknown_background_is_rejected() -> None:
    with pytest.raises(SceneryError, match="unknown background"):
        Scenery("jungle", FakeView())


def mist_layers(scenery: Scenery) -> list[DriftLayer]:
    return [layer for layer in scenery.layers if layer.kind == "mist"]


def test_see_through_clouds_come_with_the_amount_asked() -> None:
    assert mist_layers(Scenery("forest", FakeView(), seed=0)) == []  # none by default
    assert mist_layers(Scenery("space", FakeView(), seed=0, clouds=1.0)) == []  # only over grounds
    light = mist_layers(Scenery("forest", FakeView(), seed=0, clouds=0.2))
    heavy = mist_layers(Scenery("forest", FakeView(), seed=0, clouds=0.9))
    assert len(heavy) == len(params.resolve("forest").mist.layers)
    assert sum(len(layer.drifters) for layer in heavy) > sum(len(layer.drifters) for layer in light) > 0


def test_clouds_float_between_the_ground_and_the_ships() -> None:
    scenery = Scenery("mountains", FakeView(), seed=0, clouds=1.0)
    assert scenery.terrain is not None
    for layer in mist_layers(scenery):
        assert 0 < layer.depth < scenery.terrain.depth


def test_clouds_always_float_above_the_highest_ground() -> None:
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
