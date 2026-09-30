import importlib.util
import json
import sys
from pathlib import Path

import pytest

from pewpy import models

TOOL = Path(__file__).resolve().parent.parent / "tools" / "make_candidates.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("make_candidates", TOOL)
    assert spec is not None and spec.loader is not None
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    return tool


@pytest.mark.parametrize("kind", ["all", "aircraft", "industrial"])
def test_every_generated_drawing_is_a_valid_enemy_model(kind):
    drawings = load_tool().generate(12, kind, seed=3, pool_factor=2)
    assert len(drawings) == 12
    for drawing in drawings:
        rows, palette = models.parse_drawing(drawing, "candidate")
        assert models.voxel_cells(rows, palette)
        engines = models.parse_engines(drawing, "candidate")
        assert engines and all(engine.towards == "top" for engine in engines)


def test_the_same_seed_makes_the_same_batch():
    tool = load_tool()
    assert tool.generate(5, "all", seed=9, pool_factor=2) == tool.generate(5, "all", seed=9, pool_factor=2)


def test_the_tool_writes_numbered_files_and_can_append(tmp_path, monkeypatch):
    tool = load_tool()
    for argv in (["--count", "3", "--seed", "1"], ["--count", "2", "--seed", "2", "--append"]):
        monkeypatch.setattr(sys, "argv", ["make_candidates.py", "--out", str(tmp_path), "--pool", "2", *argv])
        tool.main()
    names = sorted(path.name for path in tmp_path.glob("*.json"))
    assert names == ["001.json", "002.json", "003.json", "004.json", "005.json"]
    assert json.loads((tmp_path / "005.json").read_text())["rows"]
