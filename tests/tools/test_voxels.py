import json
import shutil
import sys
from pathlib import Path

import pytest

from pewpy.graphics import models
from tools import voxels as tool

RED = [1.0, 0.0, 0.0]


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
