from typing import get_args

from pewpy.scenery.params.types import Color3, SceneryError


def test_a_mistake_says_where_it_is_if_anywhere() -> None:
    assert str(SceneryError("space.sky", "expected a list")) == "space.sky: expected a list"
    assert str(SceneryError("", "unknown background")) == "unknown background"
    assert isinstance(SceneryError("", ""), ValueError)


def test_colors_are_red_green_and_blue() -> None:
    assert get_args(Color3) == (float, float, float)
