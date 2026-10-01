import json
import shutil
import sys
from pathlib import Path

import pytest
from panda3d.core import NodePath

from pewpy.graphics import models, vox
from tools import voxels as tool

RED = [1.0, 0.0, 0.0]
BLUE = [0.0, 0.0, 1.0]


def test_a_layered_drawing_is_real_3d_with_its_middle_layer_on_the_middle_plane():
    data = {
        "layers": [["a.", ".."], ["aa", "bb"], ["..", ".b"]],  # top (nearest the camera), middle, bottom
        "palette": {"a": {"color": RED}, "b": {"color": BLUE}},
    }
    voxels = models.parse_voxels(data, "ship.json")
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
    ],
)
def test_bad_layered_drawings_are_rejected(data, problem):
    with pytest.raises(models.VoxelDrawingError, match=problem):
        models.parse_voxels(data, "ship.json")


def test_flat_drawings_still_read_as_before():
    data = {"rows": [".a.", "aba"], "palette": {"a": {"color": RED, "height": 3}, "b": {"color": BLUE, "height": 1}}}
    voxels = models.parse_voxels(data)
    rows, palette = models.parse_drawing(data)
    assert voxels.cells == models.voxel_cells(rows, palette)
    assert (voxels.width, voxels.height, voxels.scale) == (3, 2, 1)


def test_vox_files_round_trip():
    model = vox.VoxModel((3, 2, 4), [(0, 0, 0, 1), (2, 1, 3, 2)], [(255, 0, 0, 255), (0, 0, 255, 255)])
    back = vox.read(vox.write(model))
    assert back.size == model.size
    assert back.voxels == model.voxels
    assert back.palette[:2] == model.palette


def test_not_a_vox_file_is_refused():
    with pytest.raises(vox.VoxError):
        vox.read(b"nope")


def test_a_vox_model_lies_on_the_ground_seen_from_above():
    # MagicaVoxel's y goes up the screen, its z up towards the camera.
    model = vox.VoxModel((2, 2, 3), [(0, 1, 2, 1), (1, 0, 0, 1)], [(255, 0, 0, 255)])
    voxels = models.voxels_from_vox(model)
    assert (0, 0, -1) in voxels.cells  # at the back (top of the screen), on top (towards the camera)
    assert (1, 1, 1) in voxels.cells  # at the front, underneath
    assert models.voxels_from_vox(models.voxels_to_vox(voxels)).cells == voxels.cells


def test_every_model_converts_to_vox_and_back_unchanged():
    for name in ("drone", "player", "warhawk"):
        original = models.load_voxels(name)
        back = models.voxels_from_vox(vox.read(vox.write(models.voxels_to_vox(original))))
        assert set(back.cells) == set(original.cells)


def test_an_engine_can_sit_above_the_middle_plane():
    engine = models.parse_engines(
        {"rows": ["a"], "engines": [{"x": 0, "y": 0, "width": 1, "length": 1, "towards": "top", "z": 2}]}, "ship.json"
    )[0]
    assert engine.z == 2.0
    flame = models.add_flame(NodePath("ship"), engine, (1, 1), 0.5)
    assert flame.getY() == pytest.approx(-1.0)  # towards the camera (-Y)


@pytest.fixture
def model_folder(tmp_path, monkeypatch):
    """A copy of a few models, where the tool and the game read and write."""
    folder = tmp_path / "models"
    folder.mkdir()
    for name in ("drone", "player"):
        shutil.copy(Path(tool.MODELS) / f"{name}.json", folder / f"{name}.json")
    monkeypatch.setattr(tool, "MODELS", folder)
    monkeypatch.setattr(models, "data_folder", lambda: tmp_path)
    return folder


def test_a_model_exported_then_used_is_drawn_from_its_vox_file(model_folder):
    before = models.load_voxels("drone")
    tool.export("drone")
    tool.use("drone")
    data = json.loads((model_folder / "drone.json").read_text())
    assert data["vox"] == "drone.vox" and data["engines"]  # its engines are kept
    assert set(models.load_voxels("drone").cells) == set(before.cells)
    assert len(models.drawing_model("drone").findAllMatches("**/flame")) == len(data["engines"])


def test_using_a_model_that_was_never_exported_is_refused(model_folder):
    with pytest.raises(SystemExit):
        tool.use("player")


def test_a_model_turned_into_layers_keeps_its_cubes_and_engines(model_folder):
    before = models.load_voxels("player")
    tool.layers("player")
    data = json.loads((model_folder / "player.json").read_text())
    assert "layers" in data and data["engines"]
    assert models.load_voxels("player").cells.keys() == before.cells.keys()


def test_the_tool_runs_from_the_command_line(model_folder, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["voxels.py", "export", "drone", "player"])
    tool.main()
    assert (model_folder / "drone.vox").is_file() and (model_folder / "player.vox").is_file()


def test_a_finer_model_keeps_its_scale_through_the_tool(model_folder):
    data = {"scale": 2, "layers": [["aa", "aa"]], "palette": {"a": {"color": RED}}}
    (model_folder / "fine.json").write_text(json.dumps(data))
    tool.export("fine")
    tool.use("fine")
    assert models.load_voxels("fine").scale == 2
    tool.layers("fine")
    assert json.loads((model_folder / "fine.json").read_text())["scale"] == 2
