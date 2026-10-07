"""Teaching the brain, on tiny levels, in this process."""

from pathlib import Path

import numpy as np
import pytest

from pewpy.ai import files
from pewpy.ai.brain import Brain
from pewpy.ai.training import learning
from pewpy.ai.training.learning import (
    Learner,
    Report,
    check_level,
    default_workers,
    every_level,
    learn,
    level_index,
    open_levels,
    try_weights,
)

from .conftest import InlinePool

BRAIN = Brain.random(np.random.default_rng(0))


@pytest.mark.usefixtures("tiny_levels")
def test_levels_are_named_by_their_place() -> None:
    assert level_index("1-1") == 0
    assert level_index("2-2") == 3
    for wrong in ("3-1", "1-3", "x-1", "1", "0-1"):
        with pytest.raises(ValueError, match="no level"):
            level_index(wrong)
    assert every_level() == (0, 1, 2, 3)
    assert open_levels(1) == 2
    assert open_levels(9) == 4


@pytest.mark.usefixtures("tiny_levels")
def test_tries_and_checks_play_their_runs() -> None:
    assert try_weights((BRAIN.weights, BRAIN.hidden, (("vanguard", 0, 1), ("phantom", 1, 2)))) > 100  # cleared
    assert check_level((BRAIN.weights, BRAIN.hidden, "vanguard", 0, 1)) == (True, 1.0)


def test_the_cores_but_one_play(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(learning.os, "cpu_count", lambda: 8)
    assert default_workers() == 7
    monkeypatch.setattr(learning.os, "cpu_count", lambda: None)
    assert default_workers() == 1


@pytest.mark.usefixtures("tiny_levels")
def test_the_curriculum_opens_the_next_world_and_the_brain_is_saved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(learning, "CHECK_EVERY", 2)
    learner = Learner(["vanguard", "phantom"], tmp_path, InlinePool(), new=True)
    first = learner.step()
    assert first.generation == 1
    assert first.checks is None
    assert not files.brain_path(tmp_path).exists()
    second = learner.step()
    assert second.checks is not None
    assert set(second.checks) == {"vanguard", "phantom"}
    assert second.worlds == 2  # the tiny levels are cleared at once: the next world opens
    saved = files.load_training(tmp_path)
    assert saved is not None
    assert saved.generation == 2
    assert saved.history[-1]["worlds"] == 2
    again = Learner(["vanguard"], tmp_path, InlinePool())  # goes on from the saved brain
    assert again.training.generation == 2
    assert again.step().generation == 3
    while learner.training.worlds < 2 or learner.training.generation < 4:
        learner.step()
    assert learner.training.worlds == 2  # no world after the last


@pytest.mark.usefixtures("tiny_levels")
def test_training_on_the_levels_given(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(learning, "CHECK_EVERY", 1)
    monkeypatch.setattr(learning, "CHECK_RUNS", 3)
    learner = Learner(["vanguard"], tmp_path, InlinePool(), levels=(0, 3), new=True)
    report = learner.step()
    assert report.levels == 2
    assert report.checks is not None
    assert report.checks["vanguard"][0] > 0
    saved = files.load_training(tmp_path)
    assert saved is not None
    assert saved.history[-1]["levels"] == 2


@pytest.mark.usefixtures("tiny_levels")
def test_learning_reports_each_generation_and_saves_at_the_end(tmp_path: Path) -> None:
    reports: list[Report] = []
    learn(["vanguard"], 2, tmp_path, workers=1, report=reports.append, new=True)
    assert [report.generation for report in reports] == [1, 2]
    saved = files.load_training(tmp_path)
    assert saved is not None
    assert saved.generation == 2


@pytest.mark.usefixtures("tiny_levels")
def test_learning_until_stopped_saves_what_it_learned(tmp_path: Path) -> None:
    def stop(report: Report) -> None:
        if report.generation == 2:
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        learn(["vanguard"], 0, tmp_path, report=stop, new=True)
    saved = files.load_training(tmp_path)
    assert saved is not None
    assert saved.generation == 2


@pytest.mark.usefixtures("tiny_levels")
def test_stopped_before_a_generation_nothing_is_saved(tmp_path: Path) -> None:
    def stop(_report: Report) -> None:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        learn(["vanguard"], 0, tmp_path, report=stop, new=True)
    assert files.load_training(tmp_path) is None


def test_the_games_levels_and_worlds_are_trained_on() -> None:
    from pewpy.ai.training import winrate  # noqa: PLC0415 - the real levels, not the tiny ones

    assert len(learning._levels()) == sum(learning._world_sizes())
    assert winrate.places()[0][0] == "1-1"
