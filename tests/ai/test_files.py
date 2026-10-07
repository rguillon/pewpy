"""Where the AI keeps its brain."""

from pathlib import Path

import numpy as np
import pytest

from pewpy.ai import files
from pewpy.ai.brain import Brain, parameter_count


def test_the_brain_is_in_the_games_data_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(files, "data_folder", lambda: tmp_path)
    assert files.brain_folder() == tmp_path / "brain"


def test_a_brain_is_saved_and_loaded_with_its_training(tmp_path: Path) -> None:
    assert files.load_training(tmp_path) is None
    brain = Brain.random(np.random.default_rng(2))
    files.save_training(tmp_path, files.Training(brain, 30, [{"generation": 30}], worlds=2))
    loaded = files.load_training(tmp_path)
    assert loaded is not None
    assert np.array_equal(loaded.brain.weights, brain.weights)
    assert (loaded.generation, loaded.history, loaded.worlds) == (30, [{"generation": 30}], 2)


def test_a_brain_made_for_other_sensors_is_ignored(tmp_path: Path) -> None:
    files.save_training(tmp_path, files.Training(Brain(np.zeros(parameter_count(3)), inputs=3)))
    assert files.load_training(tmp_path) is None


def test_an_older_brain_trains_on_the_first_world(tmp_path: Path) -> None:
    files.save_training(tmp_path, files.Training(Brain.random(np.random.default_rng(2)), worlds=3))
    with np.load(files.brain_path(tmp_path)) as data:
        weights, hidden, inputs = data["weights"], data["hidden"], data["inputs"]
        generation, history = data["generation"], data["history"]
    np.savez(
        files.brain_path(tmp_path),
        weights=weights,
        hidden=hidden,
        inputs=inputs,
        generation=generation,
        history=history,
    )
    loaded = files.load_training(tmp_path)
    assert loaded is not None
    assert loaded.worlds == 1
