import pytest
from panda3d.core import NodePath

from pewpy.graphics.models.built.shield_bubble import shield_bubble_model
from pewpy.graphics.models.colors import main_colors, mottle, shade, tint
from pewpy.graphics.models.drawn import model, voxel_model


def test_main_colors_are_what_most_of_a_model_is_made_of() -> None:
    red, blue = (1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0)
    built = voxel_model("test", ["rrr", "rbr", "rrr"], {"r": (red, 1), "b": (blue, 1)})
    colors = main_colors(built)
    assert 1 <= len(colors) <= 3
    assert colors[0] == red  # 8 red voxels, 1 blue
    assert main_colors(built, count=1) == (red,)


def test_main_colors_skip_see_through_parts_and_look_under_empty_nodes() -> None:
    holder = NodePath("holder")
    shield_bubble_model().reparentTo(holder)  # all see-through
    assert main_colors(holder) == ((1.0, 1.0, 1.0, 1.0),)  # nothing solid: white
    model("drone").reparentTo(holder)
    assert main_colors(holder) == main_colors(model("drone"))


def test_shading_scales_a_color_at_most_to_full() -> None:
    assert shade((0.5, 0.2, 0.8, 0.5), 1.5) == pytest.approx((0.75, 0.3, 1.0, 0.5))
    assert shade((0.5, 0.2, 0.8, 1.0), 0.5) == pytest.approx((0.25, 0.1, 0.4, 1.0))


def test_tinting_multiplies_channel_by_channel_taking_the_tints_alpha() -> None:
    assert tint((0.5, 1.0, 0.8, 1.0), (1.0, 0.5, 0.5, 0.3)) == pytest.approx((0.5, 0.5, 0.4, 0.3))


def test_mottling_is_slight_and_the_same_for_the_same_cube() -> None:
    grey = (0.5, 0.5, 0.5, 1.0)
    mottled = [mottle(grey, (column, 0, 0)) for column in range(20)]
    assert all(abs(color[0] - 0.5) <= 0.5 * 0.08 + 1e-9 for color in mottled)
    assert len(set(mottled)) > 1
    assert mottle(grey, (3, 2, 1)) == mottle(grey, (3, 2, 1))
    assert mottled[0][3] == 1.0
