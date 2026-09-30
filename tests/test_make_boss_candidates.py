import json
import sys

from pewpy import models
from tools import make_boss_candidates as tool


def test_every_boss_is_a_core_with_engines_and_parts_that_load():
    for candidate in tool.generate(6, seed=2, pool_factor=2):
        rows, palette = models.parse_drawing(candidate["core"], "core")
        assert models.voxel_cells(rows, palette)
        assert len(rows[0]) >= 20
        assert models.parse_engines(candidate["core"], "core")
        for part_drawing, x, y in candidate["parts"]:
            part_rows, part_palette = models.parse_drawing(part_drawing, "part")
            assert models.voxel_cells(part_rows, part_palette)
            assert abs(x) <= len(rows[0]) / 2 and abs(y) <= len(rows) / 2  # on the core


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


def test_the_game_finds_the_boss_candidates_and_their_parts():
    names = models.boss_candidate_names()
    assert names and all(name.split("/")[1].isdigit() for name in names)  # not the parts or the layouts
    for name in names:
        rows, palette = models.load_drawing(name)
        assert models.voxel_cells(rows, palette)
        for drawing, _, _ in models.boss_candidate_parts(name):
            models.load_drawing(drawing)
