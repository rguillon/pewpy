import numpy as np

from pewpy.ai import files
from pewpy.ai.brain import Brain, parameter_count


def test_a_training_is_saved_and_loaded_back(tmp_path):
    brain = Brain(np.arange(parameter_count(), dtype=float))
    files.save_training(tmp_path, "vanguard", files.Training(brain, 12, [{"generation": 10, "cleared": 0.25}]))
    loaded = files.load_training(tmp_path, "vanguard")
    assert loaded is not None
    assert np.array_equal(loaded.brain.weights, brain.weights)
    assert (loaded.generation, loaded.history) == (12, [{"generation": 10, "cleared": 0.25}])
    assert files.load_training(tmp_path, "juggernaut") is None


def test_a_brain_made_for_other_sensors_is_ignored(tmp_path):
    files.save_training(tmp_path, "vanguard", files.Training(Brain(np.zeros(parameter_count(10)), inputs=10)))
    assert files.load_training(tmp_path, "vanguard") is None


def test_ratings_are_saved_and_loaded_back(tmp_path):
    assert files.load_ratings(tmp_path) is None
    files.save_ratings(tmp_path, {"runs": 3})
    assert files.load_ratings(tmp_path) == {"runs": 3}


def test_the_folder_is_the_users_data_folder(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert files.ai_folder() == tmp_path / "pewpy" / "ai"
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert files.ai_folder() == tmp_path / "pewpy" / "ai"
