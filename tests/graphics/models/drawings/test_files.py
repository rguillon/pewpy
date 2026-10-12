from typing import Any

import pytest

from pewpy import config
from pewpy.data import MODEL_GROUPS, data_folder
from pewpy.graphics.models.drawings.errors import VoxelDrawingError
from pewpy.graphics.models.drawings.files import DRAWINGS_FOLDER, drawing_size, load_drawing, parse_voxels, read_drawing
from pewpy.graphics.models.drawings.flat import parse_drawing
from pewpy.graphics.models.drawings.voxels import voxel_cells
from tests.graphics.models.meshes import BLUE, RED


def test_every_drawing_file_loads() -> None:
    names = []
    for group in MODEL_GROUPS:
        folder = data_folder() / DRAWINGS_FOLDER / group
        names += [file.name.removesuffix(".json") for file in folder.iterdir() if file.name.endswith(".json")]
    assert "player" in names
    assert len(names) == len(set(names))  # unique across the groups: the game names a model without its group
    parts = [f"{name}:{part}" for name in names for part in read_drawing(name)[0].get("parts", {})]
    assert any(part.startswith("avalanche:") for part in parts)  # a boss's parts, drawn in its model's file
    for name in names + parts:
        assert parse_voxels(*read_drawing(name)).cells


def test_a_flat_drawing_is_loaded_as_rows_and_a_palette() -> None:
    rows, palette = load_drawing("capsule")
    assert rows
    assert set("".join(rows)) - {".", " "} <= set(palette)


def test_a_part_the_model_doesnt_have_is_a_drawing_error() -> None:
    with pytest.raises(VoxelDrawingError, match="no part 'tail'"):
        read_drawing("player:tail")


def test_flat_drawings_read_as_their_rows_and_palette_say() -> None:
    data = {"rows": [".a.", "aba"], "palette": {"a": {"color": RED, "height": 3}, "b": {"color": BLUE, "height": 1}}}
    voxels = parse_voxels(data)
    rows, palette = parse_drawing(data)
    assert voxels.cells == voxel_cells(rows, palette)
    assert (voxels.width, voxels.height) == (3, 2)


def test_layered_drawings_are_read_too_with_or_without_engines() -> None:
    data: dict[str, Any] = {"layers": [["aa"]], "palette": {"a": {"color": RED}}}
    assert (
        parse_voxels(data).cells
        == parse_voxels({**data, "engines": []}).cells
        == {
            (0, 0, 0): (1.0, 0.0, 0.0, 1.0),
            (1, 0, 0): (1.0, 0.0, 0.0, 1.0),
        }
    )


def test_every_model_has_the_same_cubes() -> None:
    flat = {"rows": ["aa", "aa"], "palette": {"a": {"color": [1, 1, 1], "height": 1}}}
    layered = {"layers": [["aaaa"] * 4], "palette": {"a": {"color": [1, 1, 1]}}}
    assert parse_voxels(flat).size == parse_voxels(layered).size == config.MODEL_VOXEL


def test_a_scale_is_no_longer_read() -> None:
    data = {"layers": [["a"]], "palette": {"a": {"color": [1, 1, 1]}}, "scale": 2}
    with pytest.raises(VoxelDrawingError, match="expected the keys"):
        parse_voxels(data)


def test_a_model_says_the_size_it_is_meant_to_be() -> None:
    data = {"layers": [["aa", "aa", "aa"]], "palette": {"a": {"color": [1, 1, 1]}}}
    voxels = parse_voxels(data)
    assert drawing_size(data, voxels) == (2 * config.MODEL_VOXEL, 3 * config.MODEL_VOXEL)
    sized = {**data, "size": [0.1, 0.2]}
    assert drawing_size(sized, parse_voxels(sized)) == (0.1, 0.2)


@pytest.mark.parametrize("size", [[0.1], [0.1, 0], [0.1, "big"], [True, 0.1], 0.1])
def test_a_size_is_two_numbers_more_than_0(size: object) -> None:
    data = {"layers": [["a"]], "palette": {"a": {"color": [1, 1, 1]}}, "size": size}
    with pytest.raises(VoxelDrawingError, match="'size' must be 2 numbers"):
        drawing_size(data, parse_voxels(data))
