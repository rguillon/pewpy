"""The tool tidying hand-edited JSON files."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from pewpy.makers.compact_json import compact_json
from pewpy.tools import compact_json as tool
from pewpy.tools.paths import DATA, REPOSITORY

ENEMY = {"drone": {"health": 3.0, "states": [{"name": "fly", "guns": [{"pattern": "aimed", "interval": 1.5}]}]}}


def test_the_files_named_are_rewritten_compactly(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    files = [tmp_path / "a.json", tmp_path / "b.json"]
    for file in files:
        file.write_text(json.dumps(ENEMY, indent=4))
    monkeypatch.setattr(sys, "argv", ["compact_json", *map(str, files)])
    tool.main()
    for file in files:
        assert file.read_text() == compact_json(ENEMY)
        assert json.loads(file.read_text()) == ENEMY


def test_it_runs_as_a_module(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    file = tmp_path / "enemy.json"
    file.write_text(json.dumps(ENEMY, indent=4))
    monkeypatch.delitem(sys.modules, "pewpy.tools.compact_json")  # run afresh, as `python -m` does
    monkeypatch.setattr(sys, "argv", ["compact_json", str(file)])
    runpy.run_module("pewpy.tools.compact_json", run_name="__main__")
    assert file.read_text() == compact_json(ENEMY)


def test_the_tools_write_into_the_games_data_folder() -> None:
    assert DATA == REPOSITORY / "data"
    assert (DATA / "levels" / "sceneries.json").is_file()
