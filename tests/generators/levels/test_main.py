"""The command making every level of every world and writing them."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from pewpy.generators.levels import __main__ as command
from pewpy.generators.levels.__main__ import DEFAULT_SEED, LEVELS
from pewpy.generators.levels.generate import generate
from pewpy.generators.levels.worlds import WORLDS
from pewpy.generators.paths import DATA

LEVELS_MADE = generate(DEFAULT_SEED)


def test_the_games_levels_are_the_ones_the_tool_makes() -> None:
    assert LEVELS == DATA / "levels"
    for (w, n), level in LEVELS_MADE.items():
        assert json.loads((LEVELS / f"world_{w}" / f"level_{n}.json").read_text()) == level, f"{w}-{n}"


def write_levels(monkeypatch: pytest.MonkeyPatch, out: Path, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["python -m pewpy.generators.levels", "--out", str(out), *args])
    command.main()


def test_the_levels_are_written_in_place_of_the_old_worlds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "sceneries.json").write_text("{}")
    old = tmp_path / "world_9"
    old.mkdir()
    (old / "level_1.json").write_text("{}")
    write_levels(monkeypatch, tmp_path, "--seed", str(DEFAULT_SEED))
    assert not old.exists()
    assert (tmp_path / "sceneries.json").read_text() == "{}"  # the background presets stay
    assert json.loads((tmp_path / "world_1" / "world.json").read_text()) == {"name": WORLDS[0].name}
    assert json.loads((tmp_path / "world_8" / "level_6.json").read_text()) == LEVELS_MADE[8, 6]
    assert "48 levels in 8 worlds written to" in capsys.readouterr().out


def test_it_runs_as_a_module(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delitem(sys.modules, "pewpy.generators.levels.__main__")  # run afresh, as `python -m` does
    monkeypatch.setattr(sys, "argv", ["pewpy.generators.levels", "--out", str(tmp_path), "--seed", "7"])
    runpy.run_module("pewpy.generators.levels", run_name="__main__")
    assert json.loads((tmp_path / "world_1" / "level_1.json").read_text()) == generate(7)[1, 1]
