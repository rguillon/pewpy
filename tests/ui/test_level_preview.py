import pytest
from panda3d.core import NodePath

from pewpy.app import PewPewApp
from pewpy.game.level import load_levels
from pewpy.ui.level_preview import FRAME, LevelPreview, aspect2d_extent


def preview(app: PewPewApp) -> LevelPreview:
    return LevelPreview(app.scene_buffer, app.cam, app.render, app.aspect2d)


def test_aspect2d_reaches_one_along_the_shorter_side() -> None:
    aspect2d = NodePath("aspect2d")
    aspect2d.setScale(0.5, 1.0, 1.0)
    assert aspect2d_extent(aspect2d) == (2.0, 1.0)


def test_the_preview_is_a_window_of_the_game_area_hidden_until_shown(app: PewPewApp) -> None:
    shown = preview(app)
    extent_x, extent_y = aspect2d_extent(app.aspect2d)
    left, right, bottom, top = FRAME
    assert shown.share == pytest.approx((
        (left / extent_x + 1) / 2,
        (right / extent_x + 1) / 2,
        (bottom / extent_y + 1) / 2,
        (top / extent_y + 1) / 2,
    ))
    assert all(0 <= share <= 1 for share in shown.share)
    assert not shown.region.isActive()
    assert shown.frame.isHidden()
    shown.clear()


def test_a_level_is_built_once_shown_scrolled_and_forgotten(app: PewPewApp) -> None:
    shown = preview(app)
    first, second = load_levels()[:2]
    shown.update(0.1)  # nothing shown: nothing to scroll
    shown.show(0, first)
    view = shown.cache[0][0]
    assert shown.region.isActive()
    assert not shown.frame.isHidden()
    shown.show(1, second)
    assert view.root.isHidden()
    shown.show(0, first)
    assert shown.cache[0][0] is view
    terrain = view.scenery.terrain
    before = terrain.chunk_top(0) if terrain else None
    shown.update(0.5)
    assert terrain is None or terrain.chunk_top(0) != before
    shown.clear()
    assert shown.cache == {}
    assert not shown.region.isActive()
