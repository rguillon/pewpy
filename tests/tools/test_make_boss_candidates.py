import json
import sys

from pewpy.graphics import models
from tools import make_boss_candidates as tool


def test_every_boss_is_a_core_with_engines_and_parts_that_load():
    for candidate in tool.generate(6, seed=2, pool_factor=2):
        core = models.parse_voxels(candidate["core"], "core")
        assert core.cells and core.width >= 20
        assert models.parse_engines(candidate["core"], "core")
        for part_drawing, x, y in candidate["parts"]:
            assert models.parse_voxels(part_drawing, "part").cells
            assert abs(x) <= core.width / 2 and abs(y) <= core.height / 2  # on the core


def test_cores_and_parts_are_real_3d_and_parts_stand_on_the_core():
    for candidate in tool.generate(4, seed=7, pool_factor=2):
        assert "layers" in candidate["core"]
        core = models.parse_voxels(candidate["core"], "core")
        layers = [layer for _, _, layer in core.cells]
        assert -min(layers) > max(layers)  # decks and superstructure on top, a flatter underside
        for part_drawing, _, _ in candidate["parts"]:
            part = models.parse_voxels(part_drawing, "part")
            assert max(layer for _, _, layer in part.cells) < 0  # all above the middle plane: on the core


def test_the_same_seed_makes_the_same_bosses():
    assert tool.generate(3, seed=4, pool_factor=2) == tool.generate(3, seed=4, pool_factor=2)


def test_the_tool_writes_cores_parts_and_layouts_that_match(tmp_path, monkeypatch):
    for argv in (["--count", "3", "--seed", "1"], ["--count", "1", "--seed", "2", "--append"]):
        monkeypatch.setattr(sys, "argv", ["make_boss_candidates.py", "--out", str(tmp_path), "--pool", "2", *argv])
        tool.main()
    cores = sorted(path.stem for path in tmp_path.glob("*.json") if path.stem.isdigit())
    assert cores == ["001", "002", "003", "004"]
    for core in cores:
        layout = json.loads((tmp_path / f"{core}.parts.json").read_text())
        for entry in layout["parts"]:
            assert entry["drawing"].startswith(f"{core}_")
            assert (tmp_path / f"{entry['drawing']}.json").is_file()
