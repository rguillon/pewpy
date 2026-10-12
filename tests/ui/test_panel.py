import pytest
from panda3d.core import NodePath, TextNode

from pewpy.ui import panel


def test_a_card_is_a_colored_rectangle_see_through_if_its_color_is() -> None:
    root = NodePath("root")
    solid = panel.card(root, -0.5, 0.5, -0.2, 0.2, panel.FACE)
    clear = panel.card(root, -0.5, 0.5, -0.2, 0.2, panel.SCANLINE)
    bounds = solid.getTightBounds()
    assert bounds is not None
    low, high = bounds
    assert (low.x, high.x, low.z, high.z) == pytest.approx((-0.5, 0.5, -0.2, 0.2))
    assert tuple(solid.getColor()) == pytest.approx(panel.FACE, abs=1e-3)  # colors are stored compactly
    assert not solid.hasTransparency()
    assert clear.hasTransparency()


def test_a_plate_is_its_rim_bevels_face_and_four_screws() -> None:
    plate = panel.plate(NodePath("root"), -0.5, 0.5, -0.2, 0.2)
    assert plate.getNumChildren() == 4 + 4 * 2  # rim, highlight, shadow, face; a head and a slot per screw
    bounds = plate.getTightBounds()
    assert bounds is not None
    low, high = bounds
    assert (low.x, high.x) == pytest.approx((-0.5, 0.5))


def test_a_display_is_recessed_glass() -> None:
    display = panel.display(NodePath("root"), -0.3, 0.3, -0.1, 0.1)
    assert display.getNumChildren() == 4
    assert [tuple(child.getColor()) for child in display.getChildren()][2] == pytest.approx(panel.DISPLAY, abs=1e-3)


def test_scanlines_run_down_the_display_a_step_apart() -> None:
    root = NodePath("root")
    panel.scanlines(root, -0.3, 0.3, -0.1, 0.1, 0.05)
    assert root.getNumChildren() == 4


def test_texts_and_labels_can_change() -> None:
    root = NodePath("root")
    text = panel.text(root, 0.1, 0.2, 0.05, panel.AMBER, TextNode.ARight, "99")
    assert text.getText() == "99"
    text.setText("100")
    assert text.getText() == "100"
    label = panel.label(root, 0.0, 0.0, "SHIELD")
    assert label.getText() == "SHIELD"
    assert label.getTextScale()[0] == pytest.approx(panel.LABEL_SCALE)
