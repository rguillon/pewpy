import pytest
from panda3d.core import NodePath

from pewpy.ui.model_browser_view import KEYS, PART_BLINK, PART_KEYS, PART_LIT, ModelBrowserView, fit_scale


def test_with_nothing_to_show_the_frame_fills_the_view() -> None:
    view = ModelBrowserView(NodePath("camera"), NodePath("aspect2d"))
    view.show([], (0.2, 0.1))
    assert view.scaled.getScale().x == pytest.approx(fit_scale(0.2))
    view.describe("Title", "What it is", "Size", "")
    assert view.title.getText() == "Title"
    view.show([], (0.02, 0.01), least=0.1)  # a small one looks small
    assert view.scaled.getScale().x == pytest.approx(fit_scale(0.1))
    view.destroy()


def test_a_bosss_parts_blink_slowly_not_its_core() -> None:
    view = ModelBrowserView(NodePath("camera"), NodePath("aspect2d"))
    view.show([(NodePath("core"), 0.0, 0.0), (NodePath("left"), -0.1, 0.0), (NodePath("right"), 0.1, 0.0)], (0.3, 0.2))
    core, *parts = view.model.getChildren()
    assert len(parts) == len(view.parts) == 2
    assert all(tuple(part.getColorScale()) == pytest.approx(PART_LIT, abs=0.01) for part in parts)  # lit at first
    assert not core.hasColorScale()
    view.update(PART_BLINK * 0.6)
    assert not any(part.hasColorScale() for part in parts)  # then plain
    view.update(PART_BLINK * 0.5)
    assert all(part.hasColorScale() for part in parts)  # lit again
    view.destroy()


def test_the_view_lists_the_keys_of_its_browser() -> None:
    models = ModelBrowserView(NodePath("camera"), NodePath("aspect2d"))
    parts = ModelBrowserView(NodePath("camera"), NodePath("aspect2d"), PART_KEYS)
    assert (models.keys.getText(), parts.keys.getText()) == (KEYS, PART_KEYS)
    models.destroy()
    parts.destroy()
