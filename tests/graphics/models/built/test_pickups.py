from panda3d.core import TextNode

from pewpy.graphics.models.built.pickups import extra_life_model, pickup_model, repair_model
from pewpy.graphics.models.colors import main_colors
from tests.graphics.models.meshes import all_points


def test_pickup_capsules_take_the_pickup_color() -> None:
    capsule = pickup_model("B", (1.0, 0.5, 0.0, 1))
    assert (1.0, 0.5, 0.0, 1.0) in main_colors(capsule)
    assert len(all_points(capsule)) > 3 * 12


def test_a_capsule_shows_its_letter_always_facing_the_camera() -> None:
    letter = pickup_model("M", (1.0, 1.0, 1.0, 1.0)).find("letter")
    text = letter.node()
    assert isinstance(text, TextNode)
    assert text.getText() == "M"
    assert letter.getBinName() == "fixed"


def test_repairs_and_extra_lives_are_drawings() -> None:
    assert repair_model().getName() == "repair"
    assert extra_life_model().getName() == "extra_life"
    assert len(all_points(repair_model())) > 3 * 12
