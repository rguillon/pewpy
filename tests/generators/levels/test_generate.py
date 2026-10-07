"""Making every level of every world, and writing them."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from pewpy.game.enemies.kinds import FINAL_BOSSES, MINI_BOSSES
from pewpy.game.level import parse_level
from pewpy.generators.levels import __main__ as command
from pewpy.generators.levels.__main__ import DEFAULT_SEED, LEVELS
from pewpy.generators.levels.difficulty import SCROLL_SPEED, between, difficulty
from pewpy.generators.levels.enemies import GROUND
from pewpy.generators.levels.generate import generate
from pewpy.generators.levels.waves import AFTER_MINI_BOSS, BOSS_DELAY, FIRST_WAVE
from pewpy.generators.levels.worlds import WORLDS
from pewpy.generators.paths import DATA

LEVELS_MADE = generate(DEFAULT_SEED)


def test_the_games_levels_are_the_ones_the_tool_makes() -> None:
    assert LEVELS == DATA / "levels"
    for (w, n), level in LEVELS_MADE.items():
        assert json.loads((LEVELS / f"world_{w}" / f"level_{n}.json").read_text()) == level, f"{w}-{n}"


def test_the_same_seed_makes_the_same_levels_and_another_one_other_waves() -> None:
    assert generate(DEFAULT_SEED) == LEVELS_MADE
    other = generate(DEFAULT_SEED + 1)
    assert other.keys() == LEVELS_MADE.keys()
    assert other[1, 1]["waves"] != LEVELS_MADE[1, 1]["waves"]
    assert other[1, 1]["name"] == LEVELS_MADE[1, 1]["name"]


def test_every_level_is_read_by_the_game() -> None:
    for (w, n), level in LEVELS_MADE.items():
        assert parse_level(level, f"{w}-{n}").scroll_speed == round(between(SCROLL_SPEED, difficulty(w, n)), 3)


def test_each_level_has_its_mini_boss_halfway_and_its_final_boss_last() -> None:
    for (w, n), level in LEVELS_MADE.items():
        plan = WORLDS[w - 1].levels[n - 1]
        enemies = [wave["enemy"] for wave in level["waves"]]
        assert enemies.count(plan.mini_boss) == 1
        assert plan.mini_boss in MINI_BOSSES
        assert plan.final_boss in FINAL_BOSSES
        assert enemies[-1] == plan.final_boss
        waves = level["waves"]
        mini = enemies.index(plan.mini_boss)
        assert waves[0]["time"] == FIRST_WAVE
        assert waves[mini]["time"] == pytest.approx(waves[mini - 1]["time"] + BOSS_DELAY, abs=0.11)
        assert waves[mini + 1]["time"] == pytest.approx(waves[mini]["time"] + AFTER_MINI_BOSS, abs=0.11)
        assert waves[-1]["time"] == pytest.approx(waves[-2]["time"] + BOSS_DELAY, abs=0.11)


def test_worlds_without_ground_units_send_no_ground_enemies() -> None:
    for (w, _), level in LEVELS_MADE.items():
        if not WORLDS[w - 1].ground_units:
            assert not {wave["enemy"] for wave in level["waves"]} & GROUND


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
