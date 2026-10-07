"""The AI's training from the command line, its work replaced by what the tests need."""

import runpy
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from pewpy.ai import files
from pewpy.ai.brain import Brain
from pewpy.ai.training import __main__ as command
from pewpy.ai.training import learning
from pewpy.ai.training.learning import Report


def run(monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["python -m pewpy.ai.training", *args])
    command.main()


def test_learn_prints_each_generation_and_the_checks(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    calls: list[dict[str, Any]] = []

    def learn(ships: list[str], generations: int, folder: Path, _workers: int | None, report: Any, **kw: Any) -> None:  # noqa: ANN401
        calls.append({"ships": ships, "generations": generations, "folder": folder, **kw})
        report(Report(1, 10.0, 5.0))
        report(Report(10, 20.0, 8.0, {"vanguard": (0.5, 0.75)}, worlds=2))
        report(Report(20, 30.0, 9.0, {"vanguard": (1.0, 1.0)}, worlds=1, levels=1))
        report(Report(30, 30.0, 9.0, {"vanguard": (1.0, 1.0)}, worlds=1, levels=3))

    monkeypatch.setattr(command, "learn", learn)
    run(monkeypatch, "learn", "--generations", "3", "--ships", "vanguard", "--folder", str(tmp_path), "--new")
    out = capsys.readouterr().out
    assert calls == [{"ships": ["vanguard"], "generations": 3, "folder": tmp_path, "levels": None, "new": True}]
    assert "generation    1  best    10.0  mean     5.0" in out
    assert "clears  50% of the levels, gets  75% of the way" in out
    assert "(trains on 2 worlds)" in out
    assert "clears 100% of the runs" in out
    assert "(trains on 1 level)" in out
    assert "(trains on 3 levels)" in out


@pytest.mark.usefixtures("tiny_levels")
def test_learn_on_chosen_levels(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    levels: list[object] = []
    monkeypatch.setattr(command, "learn", lambda *_, **kw: levels.append(kw["levels"]))
    run(monkeypatch, "learn", "--levels", "1-2", "2-1")
    run(monkeypatch, "learn", "--levels", "all")
    assert levels == [(1, 2), learning.every_level()]
    with pytest.raises(SystemExit):
        run(monkeypatch, "learn", "--levels", "9-9")
    assert "no level 9-9" in capsys.readouterr().err


@pytest.mark.parametrize("saved", [False, True])
def test_winrate_prints_every_levels_rates_then_each_worlds(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path, saved: bool
) -> None:
    if saved:
        files.save_training(tmp_path, files.Training(Brain.random(np.random.default_rng(1)), generation=12))

    def win_rates(*args: Any) -> dict:  # noqa: ANN401 - brain, ships, runs, lives, workers, show
        show = args[-1]
        rates = {"1-1": {"vanguard": 1.0}, "1-2": {"vanguard": 0.5}, "2-1": {"vanguard": 0.0}}
        for place, rate in rates.items():
            show(place, f"Level {place}", rate)
        return rates

    monkeypatch.setattr(command, "win_rates", win_rates)
    run(monkeypatch, "winrate", "--ships", "vanguard", "--runs", "4", "--lives", "2", "--folder", str(tmp_path))
    out = capsys.readouterr().out
    assert ("generation 12" if saved else "none saved, a new one") in out
    assert "4 runs per level and ship, 2 lives each" in out
    assert "1-2  Level 1-2" in out
    assert "world 1" in out
    assert "every level" in out


def test_it_runs_as_a_module(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(learning, "learn", lambda *_, **__: None)
    monkeypatch.delitem(sys.modules, "pewpy.ai.training.__main__")  # run afresh, as `python -m` does
    monkeypatch.setattr(sys, "argv", ["pewpy.ai.training", "learn", "--folder", str(tmp_path)])
    runpy.run_module("pewpy.ai.training", run_name="__main__")
