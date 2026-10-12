from typing import Any

import pytest

from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.layered import LAYERED_KEYS, parse_layers
from tests.graphics.models.meshes import BLUE, RED


def test_a_layered_drawing_is_real_3d_with_its_middle_layer_on_the_middle_plane() -> None:
    data = {
        "layers": [["a.", ".."], ["aa", "bb"], ["..", ".b"]],  # top (nearest the camera), middle, bottom
        "palette": {"a": {"color": RED}, "b": {"color": BLUE}},
    }
    assert set(data) == LAYERED_KEYS
    voxels = parse_layers(data, "ship.json")
    assert (voxels.width, voxels.height) == (2, 2)
    assert voxels.cells[0, 0, -1] == (1.0, 0.0, 0.0, 1.0)  # the top layer: towards the camera
    assert voxels.cells[1, 1, 1] == (0.0, 0.0, 1.0, 1.0)  # the bottom one
    assert (1, 0, -1) not in voxels.cells  # holes where it's empty: overhangs and gaps are possible
    assert len(voxels.cells) == 1 + 4 + 1


@pytest.mark.parametrize(
    ("data", "problem"),
    [
        ({"layers": [], "palette": {}}, "list of layers"),
        ({"layers": [["a"], ["aa"]], "palette": {"a": {"color": RED}}}, "same rows"),
        ({"layers": [["x"]], "palette": {"a": {"color": RED}}}, "not in the palette"),
        ({"layers": [["a"]], "palette": {"a": {"color": RED, "height": 3}}}, "exactly the key 'color'"),
        ({"layers": [["a"]], "palette": ["a"]}, "map characters to a color"),
    ],
)
def test_bad_layered_drawings_are_rejected(data: dict[str, Any], problem: str) -> None:
    with pytest.raises(VoxelDrawingError, match=problem):
        parse_layers(data, "ship.json")
