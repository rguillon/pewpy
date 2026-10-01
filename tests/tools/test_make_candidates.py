import json
import sys

import pytest

from pewpy.graphics import models
from tools import make_candidates


def load_tool():
    return make_candidates


def not_an_extrusion(voxels: models.Voxels) -> bool:
    """Some columns go up further than they go down (a flat drawing's are centred on the middle plane)."""
    tops: dict[tuple[int, int], int] = {}
    bottoms: dict[tuple[int, int], int] = {}
    for column, row, layer in voxels.cells:
        tops[column, row] = min(tops.get((column, row), layer), layer)
        bottoms[column, row] = max(bottoms.get((column, row), layer), layer)
    return any(-tops[cell] != bottoms[cell] for cell in tops)


@pytest.mark.parametrize("kind", ["all", "aircraft", "industrial"])
def test_every_generated_drawing_is_a_valid_enemy_model(kind):
    drawings = load_tool().generate(12, kind, seed=3, pool_factor=2)
    assert len(drawings) == 12
    for drawing in drawings:
        assert "layers" in drawing  # every candidate is a real 3D model
        assert models.parse_voxels(drawing, "candidate").cells
        engines = models.parse_engines(drawing, "candidate")
        assert engines and all(engine.towards == "top" for engine in engines)


def test_aircraft_are_real_3d_models():
    drawings = load_tool().generate(6, "aircraft", seed=5, pool_factor=2)
    for drawing in drawings:
        assert "layers" in drawing
        voxels = models.parse_voxels(drawing, "candidate")
        layers = {layer for _, _, layer in voxels.cells}
        assert min(layers) < 0 < max(layers) or min(layers) < -1  # something above the middle plane: canopy, fins
        assert not_an_extrusion(voxels)


def test_industrial_ships_are_sculpted_in_3d():
    for drawing in load_tool().generate(8, "industrial", seed=6, pool_factor=2):
        voxels = models.parse_voxels(drawing, "candidate")
        layers = [layer for _, _, layer in voxels.cells]
        assert -min(layers) > max(layers)  # higher on top than underneath
        assert not_an_extrusion(voxels)
        assert all("z" in engine for engine in drawing["engines"])  # flames at their nozzles' height


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
    assert json.loads((tmp_path / "005.json").read_text())["layers"]
