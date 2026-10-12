import pytest

from pewpy import config
from pewpy.graphics.models.drawings.voxels import Voxels, thickest, voxel_cells
from pewpy.graphics.models.types import Palette
from tests.graphics.models.meshes import WHITE


def test_voxel_thickness_is_centered_on_the_depth() -> None:
    cells = voxel_cells(["a", "b"], {"a": (WHITE, 1), "b": (WHITE, 5)})
    assert sorted(layer for column, row, layer in cells if row == 1) == [-2, -1, 0, 1, 2]
    assert [layer for column, row, layer in cells if row == 0] == [0]


def test_dots_and_spaces_are_empty() -> None:
    assert set(voxel_cells([".a "], {"a": (WHITE, 1)})) == {(1, 0, 0)}


@pytest.mark.parametrize(
    ("rows", "palette"), [(["ab", "a"], {"a": (WHITE, 1), "b": (WHITE, 1)}), (["a"], {"a": (WHITE, 2)})]
)
def test_bad_voxel_drawings_are_rejected(rows: list[str], palette: Palette) -> None:
    with pytest.raises(ValueError, match="must"):
        voxel_cells(rows, palette)


def test_the_thickest_character_of_a_palette() -> None:
    assert thickest({"a": (WHITE, 1), "b": (WHITE, 5), "c": (WHITE, 3)}) == 5


def test_every_model_has_cubes_of_the_same_size() -> None:
    assert Voxels({}, 1, 1).size == config.MODEL_VOXEL
