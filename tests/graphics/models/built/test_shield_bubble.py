from pewpy.graphics.models.built.shield_bubble import shield_bubble_model
from pewpy.graphics.models.colors import main_colors


def test_the_shield_is_a_see_through_bubble() -> None:
    bubble = shield_bubble_model()
    assert bubble.hasTransparency()
    assert not bubble.getDepthWrite()
    assert main_colors(bubble) == ((1.0, 1.0, 1.0, 1.0),)  # nothing solid in it
