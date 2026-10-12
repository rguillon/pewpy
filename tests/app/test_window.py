import math
from typing import Any, cast

import pytest

from pewpy.app import GAME_ASPECT, PewPewApp, letterbox, window


def region_shape(window_width: int, window_height: int) -> float:
    left, right, bottom, top = letterbox(window_width, window_height)
    return (right - left) * window_width / ((top - bottom) * window_height)


@pytest.mark.parametrize(
    ("width", "height"), [(1280, 1024), (675, 900), (1200, 700), (600, 1000), (1920, 1080), (300, 2000)]
)
def test_the_game_area_keeps_its_shape_in_any_window(width: int, height: int) -> None:
    assert region_shape(width, height) == pytest.approx(GAME_ASPECT)


def test_a_wide_window_gets_bars_on_the_sides() -> None:
    left, right, bottom, top = letterbox(1600, 900)
    assert (bottom, top) == (0.0, 1.0)
    assert left == pytest.approx(1 - right)  # centered
    assert left > 0


def test_a_tall_window_gets_bars_at_the_top_and_bottom() -> None:
    left, right, bottom, top = letterbox(600, 1000)
    assert (left, right) == (0.0, 1.0)
    assert bottom == pytest.approx(1 - top)
    assert bottom > 0


def test_a_window_of_the_game_shape_has_no_bars() -> None:
    assert letterbox(1280, 1024) == pytest.approx((0.0, 1.0, 0.0, 1.0))


def test_the_letterbox_follows_the_window(app: PewPewApp, monkeypatch: pytest.MonkeyPatch) -> None:
    class Sizeless:
        def hasSize(self) -> bool:  # noqa: N802 - like Panda3D's
            return False

    monkeypatch.setattr(app, "win", Sizeless())
    app._fit_letterbox()  # the window isn't open yet: nothing to fit
    monkeypatch.undo()
    app.windowEvent(cast("Any", None))  # any window event (ShowBase only minds the ones about its own window)
    region = app.cam2d.node().getDisplayRegion(0)
    left, right, bottom, top = (region.getLeft(), region.getRight(), region.getBottom(), region.getTop())
    width, height = app.win.getXSize() * (right - left), app.win.getYSize() * (top - bottom)
    assert width / height == pytest.approx(window.GAME_ASPECT, rel=0.02)
    # The 3D view is drawn at the game area's size (the test window is small enough for it).
    assert (app.scene_buffer.getXSize(), app.scene_buffer.getYSize()) == (round(width), round(height))
    app.scene_buffer.setSize(64, 64)
    app._fit_letterbox()
    assert (app.scene_buffer.getXSize(), app.scene_buffer.getYSize()) == (round(width), round(height))
    assert app.getAspectRatio() == window.GAME_ASPECT
    assert math.isfinite(app.camera_view.area(0.0).top)


def test_the_3d_view_is_drawn_at_most_so_tall() -> None:
    assert window.scene_size(1280, 1024, max_height=1440) == (1280, 1024)
    assert window.scene_size(2700, 2160, max_height=1440) == (1800, 1440)
    assert window.scene_size(0, 0) == (1, 1)


@pytest.mark.parametrize("driver", ["d3d12", ""])
def test_leaving_the_game(app: PewPewApp, monkeypatch: pytest.MonkeyPatch, driver: str) -> None:
    exits, finals = [], []
    monkeypatch.setenv("GALLIUM_DRIVER", driver)
    monkeypatch.setattr(window.os, "_exit", exits.append)
    monkeypatch.setattr(window.ShowBase, "finalizeExit", lambda _self: finals.append(True))
    app.finalizeExit()
    assert (exits, finals) == (([0], [True]) if driver else ([], [True]))
