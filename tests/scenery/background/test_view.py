import pytest
from panda3d.core import Camera, NodePath, PerspectiveLens

from pewpy.scenery import params
from pewpy.scenery.background.scenery import Scenery
from pewpy.scenery.background.view import AREA_MARGIN, BackgroundView, CameraView, sky_color, space_color
from tests.scenery.background.views import FakeView


def camera_view() -> CameraView:
    render = NodePath("render")
    lens = PerspectiveLens()
    lens.setFov(40, 50)
    camera = render.attachNewNode(Camera("camera", lens))
    camera.setPos(0, -4, 0)  # in front of the play plane (y 0), looking into the background (+y)
    return CameraView(camera, lens, render)


def test_space_shows_its_sky_around_the_game_area() -> None:
    assert space_color() == (*params.resolve("space").sky, 1.0)


def test_the_sky_is_tinted_by_the_time_of_day() -> None:
    scenery = params.resolve("savanna")
    for time, look in scenery.times_of_day.items():
        assert sky_color(scenery, time) == pytest.approx((
            *(sky * air for sky, air in zip(scenery.sky, look.air, strict=True)),
            1.0,
        ))


def test_the_camera_sees_more_of_farther_layers_and_they_move_slower() -> None:
    view = camera_view()
    near, far = view.area(0.0), view.area(2.0)
    assert far.width > near.width > 2 * AREA_MARGIN
    assert far.height > near.height
    assert view.parallax(0.0) == pytest.approx(1.0)
    assert view.parallax(2.0) < 1.0


def test_a_space_background_draws_stars_and_drifters_where_its_layers_are() -> None:
    scenery = Scenery("space", FakeView(), seed=0)
    render = NodePath("render")
    view = BackgroundView(scenery, render)
    assert render.find("background_space") == view.root
    assert scenery.starfield is not None
    assert len(view.star_nodes) == len(scenery.starfield.layers)
    scenery.update(1.0, scroll_speed=0.3)
    view.sync()
    layer, nodes = scenery.layers[0], view.layer_nodes[0]
    assert nodes[0].getX() == pytest.approx(layer.drifters[0].x)
    assert nodes[0].getZ() == pytest.approx(layer.drifters[0].y)
    assert view.ground_nodes == []
    view.destroy()
    assert render.find("background_space").isEmpty()


def test_a_ground_is_drawn_in_strips_under_its_haze_with_its_clouds() -> None:
    scenery = Scenery("forest", FakeView(), seed=0, clouds=0.5)
    view = BackgroundView(scenery, NodePath("render"), "night" if "night" in scenery.params.times_of_day else "day")
    assert scenery.terrain is not None
    assert len(view.ground_nodes) == scenery.terrain.chunks
    assert {str(view.root.getShaderInput(name).getName()) for name in ("haze", "tint")} == {"haze", "tint"}
    assert view.mist_color != scenery.params.mist.color  # lit like the ground, in the air's color
    assert any(nodes for nodes in view.layer_nodes)  # the mist
    view.sync()
    assert view.ground_nodes[0].getZ() == pytest.approx(scenery.terrain.chunk_top(0))
