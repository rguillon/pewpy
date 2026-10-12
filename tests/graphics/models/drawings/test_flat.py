from typing import Any

import pytest

from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.flat import palette_entry, parse_drawing

DRAWING_PALETTE = {"a": {"color": [1, 0.5, 0], "height": 3}, "b": {"color": [0, 0, 1], "height": 1}}


def test_a_drawing_gives_rows_and_a_palette_of_colors_and_heights() -> None:
    rows, palette = parse_drawing({"rows": ["a.", "ab"], "palette": DRAWING_PALETTE})
    assert rows == ["a.", "ab"]
    assert palette == {"a": ((1.0, 0.5, 0.0, 1.0), 3), "b": ((0.0, 0.0, 1.0, 1.0), 1)}


def test_a_drawing_can_have_engines_a_size_weapons_and_parts() -> None:
    data = {"rows": ["a"], "palette": DRAWING_PALETTE, "engines": [], "size": [1, 1], "weapons": [], "parts": {}}
    assert parse_drawing(data) == (["a"], {"a": ((1.0, 0.5, 0.0, 1.0), 3), "b": ((0.0, 0.0, 1.0, 1.0), 1)})


@pytest.mark.parametrize(
    ("data", "problem"),
    [
        ({"rows": ["a"]}, "expected the keys"),
        ({"rows": [], "palette": DRAWING_PALETTE}, "'rows' must be a list of strings"),
        ({"rows": ["ac"], "palette": DRAWING_PALETTE}, "not in the palette"),
        ({"rows": ["a", "ab"], "palette": DRAWING_PALETTE}, "same length"),
        ({"rows": ["a"], "palette": ["a"]}, "map characters to a color and a height"),
        ({"rows": ["a"], "palette": {"a": {"color": [1, 1], "height": 1}}}, "3 numbers from 0 to 1"),
        ({"rows": ["a"], "palette": {"a": {"color": [2, 1, 1], "height": 1}}}, "3 numbers from 0 to 1"),
        ({"rows": ["a"], "palette": {"a": {"color": [1, 1, 1], "height": 2}}}, "odd whole number"),
        ({"rows": ["a"], "palette": {"a": {"color": [1, 1, 1]}}}, "expected exactly the keys"),
        ({"rows": ["a"], "palette": {"ab": {"color": [1, 1, 1], "height": 1}}}, "one character"),
    ],
)
def test_malformed_drawings_say_what_is_wrong(data: dict[str, Any], problem: str) -> None:
    with pytest.raises(VoxelDrawingError, match=problem):
        parse_drawing(data, "broken.json")


@pytest.mark.parametrize("char", [".", " ", ""])
def test_a_palette_cant_color_the_empty_characters(char: str) -> None:
    with pytest.raises(VoxelDrawingError, match=r"broken\.json: palette"):
        palette_entry(char, {"color": [1, 1, 1], "height": 1}, "broken.json")
